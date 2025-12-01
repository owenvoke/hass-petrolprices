import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PetrolPricesUpdateCoordinator
from .entity import PetrolPricesSensorEntity

DOMAIN = "petrolprices"

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

ICON = "mdi:gas-station"

SCAN_INTERVAL = timedelta(minutes=5)

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="fuel_price",
        name="Fuel price",
        icon="mdi:cash",
    ),
    SensorEntityDescription(
        key="fuel_brand_name",
        name="Fuel brand name",
        icon="mdi:fuel-station",
    ),
    SensorEntityDescription(
        key="fuel_distance_in_miles",
        name="Distance in miles",
        icon="mdi:map-marker-distance",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up all sensors for this entry."""
    coordinator: PetrolPricesUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        PetrolPricesSensorEntity(coordinator, entry, description)
        for description in SENSORS
    )
