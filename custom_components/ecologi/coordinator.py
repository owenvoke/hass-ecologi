import logging
from datetime import timedelta

import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from ecologi import Ecologi, Impact

_LOGGER = logging.getLogger(__name__)


class EcologiUpdateCoordinator(DataUpdateCoordinator[Impact]):
    """Coordinates updates between all Ecologi sensors defined."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        username: str,
        update_interval: timedelta,
    ) -> None:
        self._ecologi = Ecologi()
        self.username = username

        """Initialize the UpdateCoordinator for Ecologi sensors."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> Impact:
        async with async_timeout.timeout(5):
            return await self.hass.async_add_executor_job(
                lambda: self._ecologi.impact(self.username)
            )
