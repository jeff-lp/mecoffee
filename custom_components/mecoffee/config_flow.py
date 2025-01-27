"""Config flow for ME Coffee Machine integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ADDRESS
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)

from .const import DOMAIN, LOGGER, MECOFFEE_SERVICE_UUID


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ME Coffee Machine."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> config_entries.ConfigFlowResult:
        """Handle the bluetooth discovery step."""
        LOGGER.debug("Discovered bluetooth device: %s", discovery_info)
        
        if discovery_info.service_uuids and MECOFFEE_SERVICE_UUID in discovery_info.service_uuids:
            await self.async_set_unique_id(discovery_info.address)
            self._abort_if_unique_id_configured()
            
            LOGGER.debug("Found ME Coffee Machine: %s", discovery_info.name)
            return await self.async_step_confirm(discovery_info)
            
        return self.async_abort(reason="not_supported")

    async def async_step_confirm(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> config_entries.ConfigFlowResult:
        """Confirm discovery."""
        LOGGER.debug("Confirming discovery of: %s", discovery_info.name)
        
        return self.async_create_entry(
            title=f"ME Coffee Machine ({discovery_info.address})",
            data={
                CONF_ADDRESS: discovery_info.address,
            },
        )

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        LOGGER.debug("Starting config flow step_user with input: %s", user_input)
        
        if not user_input:
            discovered_devices = await async_discovered_service_info(self.hass)
            for discovery in discovered_devices:
                if (
                    discovery.service_uuids
                    and MECOFFEE_SERVICE_UUID in discovery.service_uuids
                ):
                    self._discovered_devices[discovery.address] = discovery
            
            if not self._discovered_devices:
                return self.async_abort(reason="no_devices_found")
            
            data_schema = vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): vol.In(
                        {
                            address: f"{discovery.name} ({address})"
                            for address, discovery in self._discovered_devices.items()
                        }
                    ),
                }
            )
            return self.async_show_form(step_id="user", data_schema=data_schema)

        discovery = self._discovered_devices[user_input[CONF_ADDRESS]]
        return await self.async_step_bluetooth(discovery)
