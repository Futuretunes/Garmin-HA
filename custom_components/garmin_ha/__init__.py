"""Garmin HA - Custom Garmin + Home Assistant Integration."""

from __future__ import annotations

import logging
import secrets

from garminconnect import Garmin

from homeassistant.components.webhook import (
    async_register as webhook_register,
    async_unregister as webhook_unregister,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_WEBHOOK_ID, DOMAIN, WEBHOOK_ID_PREFIX
from .coordinator import GarminHACoordinator
from .webhook import handle_webhook

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Garmin HA from a config entry."""
    token_data = entry.data.get("token_data")

    client = Garmin()
    try:
        await hass.async_add_executor_job(client.login, token_data)
    except Exception as err:
        _LOGGER.error("Failed to login to Garmin Connect: %s", err)
        return False

    # Update stored tokens in case they were refreshed
    new_token_data = await hass.async_add_executor_job(client.client.dumps)
    if new_token_data != token_data:
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, "token_data": new_token_data},
        )

    coordinator = GarminHACoordinator(hass, client, entry)
    await coordinator.async_config_entry_first_refresh()

    # Set up webhook for watch communication
    webhook_id = entry.data.get(CONF_WEBHOOK_ID)
    if not webhook_id:
        webhook_id = f"{WEBHOOK_ID_PREFIX}{secrets.token_hex(32)}"
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, CONF_WEBHOOK_ID: webhook_id},
        )

    webhook_register(
        hass,
        DOMAIN,
        "Garmin HA Watch",
        webhook_id,
        handle_webhook,
    )

    entry.runtime_data = {
        "coordinator": coordinator,
        "webhook_id": webhook_id,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    webhook_id = entry.runtime_data.get("webhook_id")
    if webhook_id:
        webhook_unregister(hass, webhook_id)

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
