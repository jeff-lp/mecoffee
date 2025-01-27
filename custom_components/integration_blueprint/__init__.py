"""
Custom integration to integrate integration_blueprint with Home Assistant.

For more details about this integration, please refer to
https://github.com/ludeeus/integration_blueprint
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    async_setup_scanner,
    async_get_scanner,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    LOGGER,
    MECOFFEE_SERVICE_UUID,
    MECOFFEE_CHAR_UUID,
)
from .coordinator import MeCoffeeDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import IntegrationBlueprintConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ME Coffee Machine from a config entry."""
    scanner = async_get_scanner(hass)
    
    # Set up Bluetooth scanner
    await async_setup_scanner(
        hass,
        {"scanner_mode": BluetoothScanningMode.ACTIVE},
    )
    
    # Start scanning for the coffee machine
    def handle_bluetooth_event(hass: HomeAssistant, service_info) -> None:
        """Handle Bluetooth device detection."""
        LOGGER.debug("Detected meCoffee device: %s", service_info.address)
        LOGGER.debug("Service info: %s", service_info)
        
    scanner.async_register_detection_callback(
        MECOFFEE_SERVICE_UUID,
        lambda service_info: handle_bluetooth_event(hass, service_info),
    )
    
    coordinator = MeCoffeeDataUpdateCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    LOGGER.debug("Setting up platforms with coordinator: %s", coordinator)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
