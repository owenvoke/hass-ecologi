"""Base entity for Ecologi."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EcologiUpdateCoordinator


class EcologiSensorEntity(CoordinatorEntity[EcologiUpdateCoordinator], SensorEntity):
    """An Ecologi sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcologiUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator)
        username = coordinator.username
        self.entity_description = description
        self._attr_unique_id = f"{username}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, username)},
            name=f"Ecologi ({username})",
            entry_type=DeviceEntryType.SERVICE,
            manufacturer="Ecologi",
            configuration_url=f"https://ecologi.com/{username}",
        )
