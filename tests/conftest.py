"""Fixtures for Ecologi tests."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.const import CONF_USERNAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ecologi.const import DOMAIN


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable custom integrations in every test."""


@pytest.fixture
def mock_ecologi() -> Generator[MagicMock]:
    """Patch the Ecologi client."""
    client = MagicMock()
    client.impact.return_value = {
        "trees": 120,
        "carbonOffset": 4.25,
        "carbonRemoval": 0.5,
        "habitatRestoration": 3,
        "pending": {
            "trees": 10,
            "carbonOffset": 0,
            "carbonRemoval": 0,
            "habitatRestoration": 0,
        },
    }
    with (
        patch("custom_components.ecologi.config_flow.Ecologi", return_value=client),
        patch("custom_components.ecologi.coordinator.Ecologi", return_value=client),
    ):
        yield client


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """A configured Ecologi entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Ecologi (owen)",
        unique_id="ecologi_owen",
        data={CONF_USERNAME: "owen"},
    )
