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
        if not update.advertisement.service_data:
            return

        data = update.advertisement.service_data.get(MECOFFEE_CHAR_UUID)
        if not data:
            return

        try:
            message = data.decode('utf-8').strip()
            parts = message.split()
            
            if parts[0] == MSG_TEMPERATURE and len(parts) >= 4:
                # Format: tmp <uptime> <setpoint> <current_temp> <aux> OK
                if self.entity_description.key == "temperature":
                    self._attr_native_value = float(parts[3]) * TEMPERATURE_MULTIPLIER
            
            elif parts[0] == MSG_PID and len(parts) >= 5:
                # Format: pid <p> <i> <d> <active> OK
                if self.entity_description.key == "power":
                    p_value = float(parts[1]) / 655.36
                    self._attr_native_value = p_value
            
            elif parts[0] == MSG_SHOT and len(parts) >= 3:
                # Format: sht <uptime> <duration> OK
                if self.entity_description.key == "shot_duration":
                    duration = float(parts[2]) / 1000  # Convert ms to seconds
                    self._attr_native_value = duration

        except (ValueError, IndexError, UnicodeDecodeError) as err:
            LOGGER.warning("Error parsing meCoffee message: %s", err)
            
        super()._handle_coordinator_update(update)
