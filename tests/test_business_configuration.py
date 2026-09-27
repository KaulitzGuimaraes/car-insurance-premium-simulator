from decimal import Decimal

import pytest

from app.domain.entities.car import Car
from app.domain.services.premium_calculator import PremiumCalculator
from app.domain.value_objects.money import Money
from app.domain.value_objects.percentage import Percentage
from app.domain.value_objects.rate_adjustment import RateAdjustment
from app.infrastructure.config.settings import load_settings
from app.main import create_app


def test_configured_values_reach_quote_calculation(tmp_path):
    config_path = tmp_path / "custom.yml"
    config_path.write_text(
        "gis:\n  max_adjustment: '0.05'\n  min_adjustment: '-0.04'\n"
        "pricing:\n  age_rate_increment: '0.01'\n  coverage_percentage: '0.8'\n"
        "  value_rate_increment: '0.02'\n  value_rate_step: '20000'\n"
    )
    settings = load_settings(config_path=config_path)
    service = create_app(config_path=str(config_path)).state.calculate_insurance_quote
    car = Car(
        make="Toyota",
        model="Corolla",
        value=Money(Decimal("100000")),
        year=2016,
    )
    quote, _event = service.calculate(
        broker_fee=Money(Decimal("50")),
        car=car,
        deductible_percentage=Percentage(Decimal("0.1")),
        geographic_adjustment=RateAdjustment(
            maximum=settings.gis_max_adjustment,
            minimum=settings.gis_min_adjustment,
            value=Decimal("0.05"),
        ),
        pricing_rules=settings.to_pricing_rules(),
    )

    assert quote.applied_rate > 0
    assert quote.deductible_value.value == Decimal("8000")
    assert quote.policy_limit.value == Decimal("72000")


def test_default_config_loads_outside_project_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    settings = load_settings()
    assert settings.gis_min_adjustment <= settings.gis_max_adjustment
    assert settings.to_pricing_rules().value_rate_step > 0


def test_invalid_configured_limits_fail_at_startup(tmp_path):
    config_path = tmp_path / "invalid.yml"
    config_path.write_text(
        "gis:\n  max_adjustment: -0.1\n  min_adjustment: 0.1\n"
        "pricing:\n  age_rate_increment: 0.005\n  coverage_percentage: 1\n"
        "  value_rate_increment: 0.005\n  value_rate_step: 10000\n"
    )
    with pytest.raises(ValueError, match="GIS limits"):
        create_app(config_path=str(config_path))


@pytest.mark.parametrize("value", ["0", "1000000"])
def test_money_accepts_nonnegative_values(value):
    assert Money(Decimal(value)).value == Decimal(value)


def test_money_rejects_negative_values():
    with pytest.raises(ValueError, match="Money cannot be negative"):
        Money(Decimal("-0.01"))


@pytest.mark.parametrize("value", ["0", "0.5", "1"])
def test_percentage_accepts_inclusive_range(value):
    assert Percentage(Decimal(value)).value == Decimal(value)


@pytest.mark.parametrize("value", ["-0.001", "1.001"])
def test_percentage_rejects_values_outside_range(value):
    with pytest.raises(ValueError, match="Percentage must be between"):
        Percentage(Decimal(value))


@pytest.mark.parametrize("value", ["-0.04", "0", "0.05"])
def test_rate_adjustment_accepts_configured_inclusive_range(value):
    adjustment = RateAdjustment(
        maximum=Decimal("0.05"),
        minimum=Decimal("-0.04"),
        value=Decimal(value),
    )
    assert adjustment.value == Decimal(value)


def test_rate_adjustment_rejects_values_outside_configured_range():
    with pytest.raises(ValueError, match="Rate adjustment must be between"):
        RateAdjustment(
            maximum=Decimal("0.05"),
            minimum=Decimal("-0.04"),
            value=Decimal("0.0501"),
        )
