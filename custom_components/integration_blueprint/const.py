"""Constants for ME Coffee Machine integration."""
from dataclasses import dataclass
from logging import Logger, getLogger

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature

LOGGER: Logger = getLogger(__package__)

DOMAIN = "mecoffee"
ATTRIBUTION = "Data provided by ME Coffee Machine"

# Bluetooth service and characteristic UUIDs
TEMPERATURE_SERVICE_UUID = "00000001-0000-1000-8000-00805f9b34fb"  # Replace with actual UUID
TEMPERATURE_CHAR_UUID = "00000002-0000-1000-8000-00805f9b34fb"    # Replace with actual UUID

@dataclass
class MeCoffeeSensorEntityDescription(SensorEntityDescription):
    """Describes ME Coffee sensor entity."""

SENSOR_TYPES: tuple[MeCoffeeSensorEntityDescription, ...] = (
    MeCoffeeSensorEntityDescription(
        key="temperature",
        name="Coffee Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
)
