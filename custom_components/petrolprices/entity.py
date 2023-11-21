from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PetrolPricesUpdateCoordinator, DOMAIN


class PetrolPricesSensorEntity(
    CoordinatorEntity[PetrolPricesUpdateCoordinator], SensorEntity
):
    """Representation of a PetrolPrices sensor."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator: PetrolPricesUpdateCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ):
        """Initialize the sensor and set the update coordinator."""
        super().__init__(coordinator)
        self._attr_name = description.name
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

        self.entry = entry
        self.entity_description = description

    @property
    def native_value(self):
        data = self.coordinator.data.get("data")

        if not data:
            return STATE_UNAVAILABLE

        if self.entity_description.key == "fuel_price":
            return str(data[0].get("properties").get("price", STATE_UNAVAILABLE))
        if self.entity_description.key == "fuel_brand_name":
            return str(
                data[0].get("properties").get("fuel_brand_name", STATE_UNAVAILABLE)
            )
        if self.entity_description.key == "fuel_distance_in_miles":
            return str(
                data[0]
                .get("properties")
                .get("distance_in_miles_from_given_coords", STATE_UNAVAILABLE)
            )

        return STATE_UNAVAILABLE

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            name=self.coordinator.name,
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{self.entry.entry_id}")},
            manufacturer="PetrolPrices",
            configuration_url=f"https://app.petrolprices.com",
        )
