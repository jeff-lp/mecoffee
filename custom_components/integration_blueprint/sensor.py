"""Sensor platform for ME Coffee Machine."""
from __future__ import annotations

from typing import TYPE_CHECKING

from bleak import BleakClient
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataUpdate,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSOR_TYPES, TEMPERATURE_CHAR_UUID

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ME Coffee Machine sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities(
        MeCoffeeSensor(
            coordinator=coordinator,
            entity_description=description,
        )
        for description in SENSOR_TYPES
    )


class MeCoffeeSensor(PassiveBluetoothProcessorEntity, SensorEntity):
    """ME Coffee Machine Bluetooth sensor."""

    def __init__(self, coordinator, entity_description):
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description)
        self.entity_description = entity_description

    def _handle_coordinator_update(self, update: PassiveBluetoothDataUpdate) -> None:
        """Handle updated data from the coordinator."""
        if self.entity_description.key == "temperature":
            # Convert the raw temperature data to Celsius
            raw_temp = update.device.service_data.get(TEMPERATURE_CHAR_UUID)
            if raw_temp is not None:
                self._attr_native_value = int.from_bytes(raw_temp, "little") / 100.0
        super()._handle_coordinator_update(update)
