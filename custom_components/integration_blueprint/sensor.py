"""Sensor platform for ME Coffee Machine."""
from __future__ import annotations

from typing import TYPE_CHECKING

from bleak import BleakClient
from homeassistant.const import LOGGER
from .const import (
    MECOFFEE_CHAR_UUID,
    MSG_TEMPERATURE,
    MSG_PID,
    MSG_SHOT,
    TEMPERATURE_MULTIPLIER,
)
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataUpdate,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSOR_TYPES
from .coordinator import MeCoffeeDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ME Coffee Machine sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = []
    for description in SENSOR_TYPES:
        LOGGER.debug("Setting up sensor: %s", description.key)
        sensors.append(
            MeCoffeeSensor(
                coordinator=coordinator,
                entity_description=description,
            )
        )
    async_add_entities(sensors)


class MeCoffeeSensor(SensorEntity):
    """ME Coffee Machine sensor."""

    def __init__(self, coordinator: MeCoffeeDataUpdateCoordinator, entity_description):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.entity_description = entity_description
        self._attr_unique_id = f"mecoffee_{entity_description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "mecoffee_device")},
            "name": "ME Coffee Machine",
            "manufacturer": "ME Coffee",
            "model": "ME Coffee Machine",
        }

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.entity_description.key == "temperature":
            return self.coordinator.temperature
        elif self.entity_description.key == "power":
            return self.coordinator.power
        elif self.entity_description.key == "shot_duration":
            return self.coordinator.shot_duration
        return None
