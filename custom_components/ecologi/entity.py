from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EcologiUpdateCoordinator, DOMAIN


class EcologiSensorEntity(CoordinatorEntity[EcologiUpdateCoordinator], SensorEntity):
    """Representation of an Ecologi sensor."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator: EcologiUpdateCoordinator,
        description: SensorEntityDescription,
    ):
        """Initialize the sensor and set the update coordinator."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"{self.coordinator.username} {self.entity_description.name}"
        self._attr_unique_id = f"{self.coordinator.username}_{description.key}"

    @property
    def native_value(self) -> str:
        if self.entity_description.key == "trees":
            return str(self.coordinator.data.get("trees", STATE_UNAVAILABLE))
        if self.entity_description.key == "carbon_offset":
            return str(self.coordinator.data.get("carbonOffset", STATE_UNAVAILABLE))

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            name=f"Ecologi ({self.coordinator.username})",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self.coordinator.username)},
            manufacturer="Ecologi",
            configuration_url=f"https://ecologi.com/{self.coordinator.username}",
        )
