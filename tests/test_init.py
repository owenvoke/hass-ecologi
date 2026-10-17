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

    trees = hass.states.get("sensor.ecologi_owen_trees")
    assert trees.state == "120"
    assert trees.attributes["state_class"] == "total_increasing"
    assert "unit_of_measurement" not in trees.attributes

    offset = hass.states.get("sensor.ecologi_owen_carbon_offset")
    assert offset.state == "4.25"
    assert offset.attributes["unit_of_measurement"] == "t"
    removal = hass.states.get("sensor.ecologi_owen_carbon_removal")
    assert removal.state == "0.5"
    assert removal.attributes["unit_of_measurement"] == "t"
    habitat = hass.states.get("sensor.ecologi_owen_habitat_restoration")
    assert habitat.state == "3"
    assert habitat.attributes["unit_of_measurement"] == "m²"
    assert habitat.attributes["device_class"] == "area"

    # Pending amounts are disabled by default.
    registry = er.async_get(hass)
    pending = registry.async_get("sensor.ecologi_owen_pending_trees")
    assert pending.disabled_by is er.RegistryEntryDisabler.INTEGRATION
    assert hass.states.get("sensor.ecologi_owen_pending_trees") is None
    # Unique IDs are unchanged, so existing entities are kept.
    assert er.async_get(hass).async_get("sensor.ecologi_owen_trees").unique_id == (
        "owen_trees"
    )


async def test_pending_sensors(
    hass: HomeAssistant, mock_ecologi: MagicMock, config_entry: MockConfigEntry
) -> None:
    registry = er.async_get(hass)
    registry.async_get_or_create(
        "sensor",
        "ecologi",
        "owen_pending_trees",
        suggested_object_id="ecologi_owen_pending_trees",
        disabled_by=None,
    )
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    pending = hass.states.get("sensor.ecologi_owen_pending_trees")
    assert pending.state == "10"
    assert pending.attributes["state_class"] == "measurement"


async def test_older_api_response(
    hass: HomeAssistant, mock_ecologi: MagicMock, config_entry: MockConfigEntry
) -> None:
    """Fields the API didn't always return are unknown rather than errors."""
    mock_ecologi.impact.return_value = {"trees": 120, "carbonOffset": 4.25}
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get("sensor.ecologi_owen_trees").state == "120"
    assert hass.states.get("sensor.ecologi_owen_carbon_removal").state == "unknown"


async def test_setup_retries_on_network_error(
    hass: HomeAssistant, mock_ecologi: MagicMock, config_entry: MockConfigEntry
) -> None:
    mock_ecologi.impact.side_effect = requests.ConnectionError()
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY
