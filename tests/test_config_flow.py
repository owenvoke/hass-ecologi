"""Tests for the Ecologi config and options flows."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests
from ecologi import NotFoundException
from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ecologi.const import DOMAIN


async def test_user_flow(hass: HomeAssistant, mock_ecologi: MagicMock) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_USERNAME: "owen"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Ecologi (owen)"


@pytest.mark.parametrize(
    ("side_effect", "errors"),
    [
        (NotFoundException(), {CONF_USERNAME: "invalid_username"}),
        (requests.ConnectionError(), {"base": "cannot_connect"}),
        (ValueError(), {"base": "unknown"}),
    ],
)
async def test_user_flow_errors(
    hass: HomeAssistant,
    mock_ecologi: MagicMock,
    side_effect: Exception,
    errors: dict[str, str],
) -> None:
    mock_ecologi.impact.side_effect = side_effect
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_USERNAME: "owen"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == errors


async def test_options_flow_reloads(
    hass: HomeAssistant, mock_ecologi: MagicMock, config_entry: MockConfigEntry
) -> None:
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 60}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert config_entry.runtime_data.update_interval.total_seconds() == 3600
