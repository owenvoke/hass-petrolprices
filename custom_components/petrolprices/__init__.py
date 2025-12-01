"""The PetrolPrices integration"""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    Platform,
    CONF_API_TOKEN,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_RADIUS,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import HomeAssistant
from petrolprices import FuelType

from .const import (
    DOMAIN,
    CONF_FUEL_TYPE,
    DEFAULT_FUEL_TYPE,
    DEFAULT_RADIUS,
    DEFAULT_SCAN_INTERVAL,
    AVAILABLE_FUEL_TYPES_MAP,
)
from .coordinator import PetrolPricesUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    petrolprices_coordinator = PetrolPricesUpdateCoordinator(
        hass=hass,
        name=config_entry.title,
        api_token=config_entry.data[CONF_API_TOKEN],
        latitude=config_entry.data[CONF_LATITUDE],
        longitude=config_entry.data[CONF_LONGITUDE],
        fuel_type=fuel_type_from_name(config_entry.data[CONF_FUEL_TYPE]),
        radius=config_entry.options.get(CONF_RADIUS, DEFAULT_RADIUS),
        update_interval=timedelta(
            minutes=(
                config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            )
        ),
    )

    await petrolprices_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = petrolprices_coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    config_entry.async_on_unload(
        config_entry.add_update_listener(options_update_listener)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def options_update_listener(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


def fuel_type_from_name(name: str) -> FuelType:
    return AVAILABLE_FUEL_TYPES_MAP[name]
