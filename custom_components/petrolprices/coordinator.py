from __future__ import absolute_import

import logging
from datetime import timedelta

import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from petrolprices import PetrolPrices, SearchEntriesCollection, FuelType

_LOGGER = logging.getLogger(__name__)


class PetrolPricesUpdateCoordinator(DataUpdateCoordinator[SearchEntriesCollection]):
    """Coordinates updates between all PetrolPrices sensors defined."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        api_token: str,
        latitude: str,
        longitude: str,
        fuel_type: FuelType,
        radius: int,
        update_interval: timedelta,
    ) -> None:
        self._petrolprices = PetrolPrices(api_token=api_token)
        self._latitude = latitude
        self._longitude = longitude
        self._fuel_type = fuel_type
        self._radius = radius

        """Initialize the UpdateCoordinator for PetrolPrices sensors."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> SearchEntriesCollection:
        async with async_timeout.timeout(5):
            return await self.hass.async_add_executor_job(
                lambda: self._petrolprices.search(
                    latitude=float(self._latitude),
                    longitude=float(self._longitude),
                    fuel_type=self._fuel_type,
                    max_distance=self._radius,
                )
            )
