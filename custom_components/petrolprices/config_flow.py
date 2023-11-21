from __future__ import annotations

import logging
from datetime import timedelta
from hashlib import md5
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlow, ConfigEntry
from homeassistant.const import (
    CONF_API_TOKEN,
    CONF_SCAN_INTERVAL,
    CONF_LONGITUDE,
    CONF_LATITUDE,
    CONF_RADIUS,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectSelectorConfig,
    SelectSelector,
    SelectSelectorMode,
)
from petrolprices import (
    PetrolPrices,
    NotFoundException,
    UnauthorizedException,
)

import homeassistant.helpers.config_validation as cv

from . import PetrolPricesUpdateCoordinator
from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    CONF_FUEL_TYPE,
    DEFAULT_RADIUS,
    AVAILABLE_FUEL_TYPES,
)

_LOGGER = logging.getLogger(__name__)


class PetrolPricesConfigFlow(ConfigFlow, domain=DOMAIN):
    """The configuration flow for a PetrolPrices system."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = {}
        if user_input is not None:
            try:
                search_entries = await self.hass.async_add_executor_job(
                    lambda: PetrolPrices(api_token=user_input[CONF_API_TOKEN]).search(
                        latitude=user_input[CONF_LATITUDE],
                        longitude=user_input[CONF_LONGITUDE],
                    )
                )
                if search_entries:
                    # Make sure we're not configuring the same device
                    latitude_hash = md5(
                        str(user_input[CONF_LATITUDE]).encode("utf-8")
                    ).hexdigest()
                    longitude_hash = md5(
                        str(user_input[CONF_LONGITUDE]).encode("utf-8")
                    ).hexdigest()
                    fuel_type = user_input[CONF_FUEL_TYPE]

                    await self.async_set_unique_id(
                        f"petrolprices_{latitude_hash}_{longitude_hash}_{fuel_type}"
                    )
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"PetrolPrices ({fuel_type})",
                        data=user_input,
                    )
            except UnauthorizedException:
                errors[CONF_API_TOKEN] = "invalid_api_token"
            except NotFoundException:
                errors[CONF_API_TOKEN] = "not_found"
            else:
                errors[CONF_API_TOKEN] = "server_error"

        config_schema = vol.Schema(
            {
                vol.Required(CONF_API_TOKEN): cv.string,
                vol.Inclusive(
                    CONF_LATITUDE, "coordinates", default=self.hass.config.latitude
                ): cv.latitude,
                vol.Inclusive(
                    CONF_LONGITUDE, "coordinates", default=self.hass.config.longitude
                ): cv.longitude,
                vol.Required(CONF_FUEL_TYPE): SelectSelector(
                    SelectSelectorConfig(
                        options=AVAILABLE_FUEL_TYPES,
                        sort=True,
                        mode=SelectSelectorMode.LIST,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=config_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> PetrolPricesOptionsFlowHandler:
        return PetrolPricesOptionsFlowHandler(config_entry)


class PetrolPricesOptionsFlowHandler(OptionsFlow):
    """Config flow options handler for PetrolPrices."""

    def __init__(self, config_entry: ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry
        # Cast from MappingProxy to dict to allow update.
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            self.options.update(user_input)
            coordinator: PetrolPricesUpdateCoordinator = self.hass.data[DOMAIN][
                self.config_entry.entry_id
            ]

            update_interval = timedelta(
                minutes=self.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            )
            radius = self.options.get(CONF_RADIUS, DEFAULT_RADIUS)

            _LOGGER.debug(
                "Updating coordinator, update_interval: %s, radius: %s",
                update_interval,
                radius,
            )

            coordinator.update_interval = update_interval

            self.hass.data[DOMAIN][self.config_entry.entry_id] = coordinator

            return self.async_create_entry(title="", data=self.options)

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1)),
                vol.Required(
                    CONF_RADIUS,
                    default=self.config_entry.options.get(CONF_RADIUS, DEFAULT_RADIUS),
                ): cv.positive_int,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )
