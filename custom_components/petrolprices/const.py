"""Constants for the PetrolPrices integration."""

from typing import Final

from petrolprices import FuelType

DOMAIN: Final = "petrolprices"

CONF_FUEL_TYPE: Final = "fuel_type"

DEFAULT_FUEL_TYPE: Final = FuelType.Unleaded
DEFAULT_RADIUS: Final = 250
DEFAULT_SCAN_INTERVAL: Final = 86400  # Daily

AVAILABLE_FUEL_TYPES: Final = ["Unleaded", "Diesel", "Super Unleaded", "Premium Diesel"]

AVAILABLE_FUEL_TYPES_MAP: Final = {
    "Unleaded": FuelType.Unleaded,
    "Diesel": FuelType.Diesel,
    "Super Unleaded": FuelType.SuperUnleaded,
    "Premium Diesel": FuelType.PremiumDiesel,
}
