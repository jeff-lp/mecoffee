"""Constants for ME Coffee Machine integration."""
from dataclasses import dataclass
from logging import Logger, getLogger
from pathlib import Path
import json

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature

LOGGER: Logger = getLogger(__package__)

MANIFEST_PATH = Path(__file__).parent / "manifest.json"
with MANIFEST_PATH.open() as manifest_file:
    manifest = json.load(manifest_file)
    DOMAIN = manifest["domain"]

ATTRIBUTION = "Data provided by ME Coffee Machine"

# Bluetooth service and characteristic UUIDs
# Bluetooth UUIDs for meCoffee
MECOFFEE_SERVICE_UUID = "0000180f-0000-1000-8000-00805f9b34fb"
MECOFFEE_CHAR_UUID = "00002a19-0000-1000-8000-00805f9b34fb"

# Message types
MSG_TEMPERATURE = "tmp"
MSG_PID = "pid"
MSG_SHOT = "sht"

# Message parsing
TEMPERATURE_MULTIPLIER = 0.01  # Temperature values are in °C/100

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
