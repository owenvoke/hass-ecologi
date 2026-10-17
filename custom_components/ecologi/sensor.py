"""Sensors for Ecologi."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfArea
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from ecologi import Impact

from .coordinator import EcologiConfigEntry
from .entity import EcologiSensorEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class EcologiSensorEntityDescription(SensorEntityDescription):
    """Describes an Ecologi sensor."""

    value_fn: Callable[[Impact], int | float | None]


# Tonnes of CO₂ equivalent. Home Assistant has no tonnes unit, so unlike the
# area this isn't convertible.
UNIT_TONNES = "t"


@dataclass(frozen=True, kw_only=True)
class Measure:
    """How Ecologi reports one kind of impact."""

    field: str
    unit: str | None = None
    device_class: SensorDeviceClass | None = None


# Totals only ever grow, while pending amounts drop as they're fulfilled.
TOTALS = {
    "trees": Measure(field="trees"),
    "carbon_offset": Measure(field="carbonOffset", unit=UNIT_TONNES),
    "carbon_removal": Measure(field="carbonRemoval", unit=UNIT_TONNES),
    "habitat_restoration": Measure(
        field="habitatRestoration",
        unit=UnitOfArea.SQUARE_METERS,
        device_class=SensorDeviceClass.AREA,
    ),
}


def _pending(field: str) -> Callable[[Impact], int | float | None]:
    return lambda impact: (impact.get("pending") or {}).get(field)


SENSORS: tuple[EcologiSensorEntityDescription, ...] = (
    *(
        EcologiSensorEntityDescription(
            key=key,
            translation_key=key,
            device_class=measure.device_class,
            native_unit_of_measurement=measure.unit,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value_fn=lambda impact, field=measure.field: impact.get(field),
        )
        for key, measure in TOTALS.items()
    ),
    *(
        EcologiSensorEntityDescription(
            key=f"pending_{key}",
            translation_key=f"pending_{key}",
            device_class=measure.device_class,
            native_unit_of_measurement=measure.unit,
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=False,
            value_fn=_pending(measure.field),
        )
        for key, measure in TOTALS.items()
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
