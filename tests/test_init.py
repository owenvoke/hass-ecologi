"""Tests for Ecologi setup and sensors."""

from __future__ import annotations

from unittest.mock import MagicMock

import requests
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_sensors(
    hass: HomeAssistant, mock_ecologi: MagicMock, config_entry: MockConfigEntry
) -> None:
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get("sensor.ecologi_owen_trees").state == "120"
    assert hass.states.get("sensor.ecologi_owen_carbon_offset").state == "4.25"
    # Unique IDs are unchanged, so existing entities are kept.
    assert er.async_get(hass).async_get("sensor.ecologi_owen_trees").unique_id == (
        "owen_trees"
    )


async def test_setup_retries_on_network_error(
    hass: HomeAssistant, mock_ecologi: MagicMock, config_entry: MockConfigEntry
) -> None:
    mock_ecologi.impact.side_effect = requests.ConnectionError()
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY
