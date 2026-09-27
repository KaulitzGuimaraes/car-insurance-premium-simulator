from decimal import Decimal
from pathlib import Path

import yaml

from app.domain.value_objects.pricing_rules import PricingRules

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[3] / "config.yml"


class Settings:
    def __init__(
        self,
        age_rate_increment: Decimal,
        coverage_percentage: Decimal,
        gis_max_adjustment: Decimal,
        gis_min_adjustment: Decimal,
        value_rate_increment: Decimal,
        value_rate_step: Decimal,
    ):
        if (
            not gis_max_adjustment.is_finite()
            or not gis_min_adjustment.is_finite()
            or gis_min_adjustment > gis_max_adjustment
        ):
            raise ValueError("GIS limits must be finite and minimum <= maximum")

        self._age_rate_increment = age_rate_increment
        self._coverage_percentage = coverage_percentage
        self._gis_max_adjustment = gis_max_adjustment
        self._gis_min_adjustment = gis_min_adjustment
        self._value_rate_increment = value_rate_increment
        self._value_rate_step = value_rate_step

    @property
    def age_rate_increment(self) -> Decimal:
        return self._age_rate_increment

    @property
    def coverage_percentage(self) -> Decimal:
        return self._coverage_percentage

    @property
    def gis_max_adjustment(self) -> Decimal:
        return self._gis_max_adjustment

    @property
    def gis_min_adjustment(self) -> Decimal:
        return self._gis_min_adjustment

    def to_pricing_rules(self) -> PricingRules:
        return PricingRules(
            age_rate_increment=self.age_rate_increment,
            coverage_percentage=self.coverage_percentage,
            value_rate_increment=self.value_rate_increment,
            value_rate_step=self.value_rate_step,
        )

    @property
    def value_rate_increment(self) -> Decimal:
        return self._value_rate_increment

    @property
    def value_rate_step(self) -> Decimal:
        return self._value_rate_step


def load_settings(config_path: str | Path = DEFAULT_CONFIG_PATH) -> Settings:
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    pricing = config["pricing"]
    gis = config["gis"]

    return Settings(
        age_rate_increment=Decimal(str(pricing["age_rate_increment"])),
        coverage_percentage=Decimal(str(pricing["coverage_percentage"])),
        gis_max_adjustment=Decimal(str(gis["max_adjustment"])),
        gis_min_adjustment=Decimal(str(gis["min_adjustment"])),
        value_rate_increment=Decimal(str(pricing["value_rate_increment"])),
        value_rate_step=Decimal(str(pricing["value_rate_step"])),
    )
