"""DataUpdateCoordinator for meCoffee."""
from __future__ import annotations

from datetime import timedelta
import asyncio
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import LOGGER

from .const import DOMAIN, MECOFFEE_CHAR_UUID

class MeCoffeeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching meCoffee data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        LOGGER.debug("Initializing MeCoffeeDataUpdateCoordinator")
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=1),
        )
        LOGGER.debug("MeCoffeeDataUpdateCoordinator initialized")
        self._temperature: float | None = None
        self._power: float | None = None
        self._shot_duration: float | None = None

    @property
    def temperature(self) -> float | None:
        """Return the current temperature."""
        return self._temperature

    @property
    def power(self) -> float | None:
        """Return the current power."""
        return self._power

    @property
    def shot_duration(self) -> float | None:
        """Return the current shot duration."""
        return self._shot_duration

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data."""
        LOGGER.debug("Running data update")
        try:
            LOGGER.debug("Current values - Temp: %s, Power: %s, Shot Duration: %s",
                        self._temperature, self._power, self._shot_duration)
            return {
                "temperature": self._temperature,
                "power": self._power,
                "shot_duration": self._shot_duration,
            }
        except Exception as err:
            LOGGER.error("Error updating data: %s", err)
            raise

    def handle_bluetooth_data(self, data: bytes) -> None:
        """Handle received Bluetooth data."""
        try:
            message = data.decode('utf-8').strip()
            LOGGER.debug("Processing meCoffee message: %s", message)
            parts = message.split()

            if not parts:
                return

            if parts[0] == "tmp" and len(parts) >= 4:
                self._temperature = float(parts[3]) * 0.01  # Convert to Celsius
            elif parts[0] == "pid" and len(parts) >= 5:
                self._power = float(parts[1]) / 655.36  # Convert to percentage
            elif parts[0] == "sht" and len(parts) >= 3:
                self._shot_duration = float(parts[2]) / 1000  # Convert to seconds

            self.async_set_updated_data(self._async_update_data())
            
        except (ValueError, IndexError, UnicodeDecodeError) as err:
            LOGGER.warning("Error parsing meCoffee message: %s", err)
