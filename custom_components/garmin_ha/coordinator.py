"""Data update coordinator for Garmin HA."""

from __future__ import annotations

from datetime import date, timedelta
import logging
from typing import Any

from garminconnect import Garmin, GarminConnectAuthenticationError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


def _resolve_nested_key(data: dict, key: str) -> Any:
    """Resolve a dot-separated key path like 'sleepScores.overall.value'."""
    parts = key.split(".")
    value = data
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    return value


class GarminHACoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate Garmin Connect data fetching."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: Garmin,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
            config_entry=config_entry,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Garmin Connect API."""
        today = date.today().isoformat()
        data: dict[str, Any] = {}

        try:
            data["daily_summary"] = await self._fetch(
                "get_user_summary", today
            )
            data["heart_rate"] = await self._fetch(
                "get_heart_rates", today
            )
            data["body_battery"] = await self._fetch(
                "get_body_battery", today, today
            )
            data["stress"] = await self._fetch(
                "get_all_day_stress", today
            )
            data["sleep"] = await self._fetch(
                "get_sleep_data", today
            )
            data["spo2"] = await self._fetch(
                "get_spo2_data", today
            )
            data["respiration"] = await self._fetch(
                "get_respiration_data", today
            )
            data["training_readiness"] = await self._fetch(
                "get_training_readiness", today
            )
            data["hrv"] = await self._fetch(
                "get_hrv_data", today
            )
            data["last_activity"] = await self._fetch_last_activity()

        except GarminConnectAuthenticationError as err:
            raise ConfigEntryAuthFailed(
                "Garmin authentication failed"
            ) from err
        except Exception as err:
            raise UpdateFailed(
                f"Error fetching Garmin data: {err}"
            ) from err

        return data

    async def _fetch(self, method_name: str, *args: Any) -> dict[str, Any]:
        """Call a garminconnect method in the executor."""
        try:
            method = getattr(self.client, method_name)
            result = await self.hass.async_add_executor_job(method, *args)
            return result if isinstance(result, dict) else {}
        except GarminConnectAuthenticationError:
            raise
        except Exception as err:
            _LOGGER.debug("Failed to fetch %s: %s", method_name, err)
            return {}

    async def _fetch_last_activity(self) -> dict[str, Any]:
        """Fetch the most recent activity."""
        try:
            activities = await self.hass.async_add_executor_job(
                self.client.get_activities, 0, 1
            )
            if activities and len(activities) > 0:
                return activities[0]
        except GarminConnectAuthenticationError:
            raise
        except Exception as err:
            _LOGGER.debug("Failed to fetch last activity: %s", err)
        return {}

    def get_value(self, source: str, value_key: str) -> Any:
        """Get a value from the coordinator data by source and key."""
        if not self.data:
            return None
        source_data = self.data.get(source, {})
        if not source_data:
            return None
        return _resolve_nested_key(source_data, value_key)
