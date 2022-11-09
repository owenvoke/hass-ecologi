import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EcologiUpdateCoordinator
from .entity import EcologiSensorEntity

DOMAIN = "ecologi"

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

ICON = "mdi:forest"

SCAN_INTERVAL = timedelta(minutes=5)

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="trees",
        name="Trees",
        icon="mdi:forest",
    ),
    SensorEntityDescription(
        key="carbon_offset", name="Carbon Offset", icon="mdi:molecule-co2"
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up all sensors for this entry."""
    coordinator: EcologiUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        EcologiSensorEntity(coordinator, description) for description in SENSORS
    )
