"""Sensor platform for Garmin HA."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ALL_SENSORS, DOMAIN, GarminSensorEntityDescription
from .coordinator import GarminHACoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Garmin sensors from a config entry."""
    coordinator: GarminHACoordinator = entry.runtime_data["coordinator"]

    entities = [
        GarminSensor(coordinator, description, entry)
        for description in ALL_SENSORS
    ]
    async_add_entities(entities)


class GarminSensor(CoordinatorEntity[GarminHACoordinator], SensorEntity):
    """Representation of a Garmin sensor."""

    entity_description: GarminSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GarminHACoordinator,
        description: GarminSensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Garmin Watch",
            manufacturer="Garmin",
            model="Epix 2",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        return self.coordinator.get_value(
            self.entity_description.source,
            self.entity_description.value_key,
        )
