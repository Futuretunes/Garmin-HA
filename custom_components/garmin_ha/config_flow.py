"""Config flow for Garmin HA."""

from __future__ import annotations

import logging
from typing import Any

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

from .const import DOMAIN
from .widget_login import WidgetAuth, WidgetLoginError

_LOGGER = logging.getLogger(__name__)

CONF_MFA_CODE = "mfa_code"


class GarminHAConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Garmin HA."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._client: Garmin | None = None
        self._email: str = ""
        self._password: str = ""
        self._widget_auth: WidgetAuth | None = None

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._email = user_input[CONF_EMAIL]
            self._password = user_input[CONF_PASSWORD]

            # Try widget SSO first — it doesn't burn rate-limit quota
            # like garminconnect's 4 login strategies do.
            try:
                self._widget_auth = WidgetAuth()
                token_data = await self.hass.async_add_executor_job(
                    self._widget_auth.login, self._email, self._password
                )
                if token_data is None:
                    return await self.async_step_mfa()
                return await self._async_finish_login_with_tokens(token_data)
            except Exception as widget_err:
                _LOGGER.warning(
                    "Widget SSO login failed (%s: %s), "
                    "falling back to standard login",
                    type(widget_err).__name__, widget_err,
                )
                self._widget_auth = None

            # Fallback: standard garminconnect login
            try:
                self._client = Garmin(
                    self._email, self._password, return_on_mfa=True
                )
                mfa_status, _ = await self.hass.async_add_executor_job(
                    self._client.login
                )

                if mfa_status is not None:
                    return await self.async_step_mfa()

                return await self._async_finish_login()

            except GarminConnectAuthenticationError as err:
                _LOGGER.error("Garmin auth failed: %s", err)
                errors["base"] = "invalid_auth"
            except GarminConnectTooManyRequestsError:
                errors["base"] = "too_many_requests"
            except GarminConnectConnectionError as err:
                _LOGGER.error("Garmin connection failed: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during login")
                errors["base"] = "unknown"

        return self._show_user_form(errors)

    async def async_step_mfa(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle MFA verification step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            mfa_code = user_input[CONF_MFA_CODE]
            try:
                if self._widget_auth:
                    token_data = await self.hass.async_add_executor_job(
                        self._widget_auth.submit_mfa, mfa_code
                    )
                    return await self._async_finish_login_with_tokens(token_data)
                else:
                    await self.hass.async_add_executor_job(
                        self._client.client.resume_login, None, mfa_code
                    )
                    return await self._async_finish_login()
            except (
                GarminConnectAuthenticationError,
                WidgetLoginError,
            ):
                errors["base"] = "invalid_mfa"
            except Exception:
                _LOGGER.exception("Unexpected error during MFA verification")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="mfa",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MFA_CODE): str,
                }
            ),
            errors=errors,
        )

    async def _async_finish_login(self) -> ConfigFlowResult:
        """Dump tokens and create the config entry."""
        token_data = await self.hass.async_add_executor_job(
            self._client.client.dumps
        )
        return await self._async_finish_login_with_tokens(token_data)

    async def _async_finish_login_with_tokens(
        self, token_data: str
    ) -> ConfigFlowResult:
        """Create the config entry from token data."""
        await self.async_set_unique_id(self._email)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=self._email,
            data={
                CONF_EMAIL: self._email,
                "token_data": token_data,
            },
        )

    async def async_step_reauth(
        self,
        entry_data: dict[str, Any],
    ) -> ConfigFlowResult:
        """Handle reauthorization."""
        return await self.async_step_user()

    def _show_user_form(
        self, errors: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Show the credentials form."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors or {},
        )
