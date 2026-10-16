"""Sensors for Ecologi."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ecologi import Impact
from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EcologiConfigEntry
from .entity import EcologiSensorEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class EcologiSensorEntityDescription(SensorEntityDescription):
    """Describes an Ecologi sensor."""

    value_fn: Callable[[Impact], int | float | None]


SENSORS: tuple[EcologiSensorEntityDescription, ...] = (
    EcologiSensorEntityDescription(
        key="trees",
        translation_key="trees",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda impact: impact.get("trees"),
    ),
    EcologiSensorEntityDescription(
        key="carbon_offset",
        translation_key="carbon_offset",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda impact: impact.get("carbonOffset"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EcologiConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensors."""
    async_add_entities(
        EcologiSensor(entry.runtime_data, description) for description in SENSORS
    )


class EcologiSensor(EcologiSensorEntity):
    """An Ecologi impact sensor."""

    entity_description: EcologiSensorEntityDescription

    @property
    def native_value(self) -> int | float | None:
        """Return the sensor's value."""
        return self.entity_description.value_fn(self.coordinator.data)
