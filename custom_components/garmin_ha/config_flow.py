"""Config flow for Garmin HA."""

from __future__ import annotations

import logging
from typing import Any

from garminconnect import Garmin, GarminConnectAuthenticationError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class GarminHAConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Garmin HA."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._client: Garmin | None = None
        self._email: str = ""
        self._password: str = ""

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._email = user_input[CONF_EMAIL]
            self._password = user_input[CONF_PASSWORD]

            try:
                self._client = await self.hass.async_add_executor_job(
                    self._try_login, self._email, self._password
                )
                token_data = await self.hass.async_add_executor_job(
                    self._client.garth.dumps
                )

                await self.async_set_unique_id(self._email)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=self._email,
                    data={
                        CONF_EMAIL: self._email,
                        "token_data": token_data,
                    },
                )
            except GarminConnectAuthenticationError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected error during login")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self,
        entry_data: dict[str, Any],
    ) -> ConfigFlowResult:
        """Handle reauthorization."""
        return await self.async_step_user()

    @staticmethod
    def _try_login(email: str, password: str) -> Garmin:
        """Attempt to log in to Garmin Connect."""
        client = Garmin(email, password)
        client.login()
        return client
