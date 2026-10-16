"""Data update coordinator for Ecologi."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import requests
from ecologi import Ecologi, EcologiException, Impact
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30

type EcologiConfigEntry = ConfigEntry[EcologiUpdateCoordinator]


class EcologiUpdateCoordinator(DataUpdateCoordinator[Impact]):
    """Fetch a user's Ecologi impact."""

    config_entry: EcologiConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: EcologiConfigEntry) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(
                minutes=int(
                    config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                )
            ),
        )
        self._ecologi = Ecologi()
        self.username: str = config_entry.data[CONF_USERNAME]

    async def _async_update_data(self) -> Impact:
        """Fetch the latest impact."""
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                return await self.hass.async_add_executor_job(
                    self._ecologi.impact, self.username
                )
        except (EcologiException, requests.RequestException, TimeoutError) as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
                translation_placeholders={"error": str(err)},
            ) from err
