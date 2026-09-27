from datetime import date
from decimal import Decimal

import pytest

from app.domain.entities.car import Car
from app.domain.services.premium_calculator import PremiumCalculator
from app.domain.value_objects.money import Money
from app.domain.value_objects.percentage import Percentage
from app.domain.value_objects.pricing_rules import PricingRules


@pytest.fixture
def calculator():
    return PremiumCalculator()


@pytest.fixture
def car():
    return Car(
        make="Toyota",
        model="Corolla",
        value=Money(Decimal("100000")),
        year=2016,
    )


@pytest.fixture
def rules():
    return PricingRules(
        age_rate_increment=Decimal("0.005"),
        coverage_percentage=Decimal("1.0"),
        value_rate_increment=Decimal("0.005"),
        value_rate_step=Decimal("10000"),
    )


def test_age_rate(calculator, car, rules):
    assert calculator.calculate_age_rate(car=car, current_year=2026, rules=rules) == Decimal("0.05")


def test_applied_rate(calculator, car, rules):
    assert calculator.calculate_applied_rate(
        car=car, current_year=2026, geographic_adjustment=None, rules=rules
    ) == Decimal("0.10")


def test_future_car_year_is_rejected():
    with pytest.raises(ValueError, match="Year cannot be greater than current year"):
        Car(
            make="Toyota",
            model="Corolla",
            value=Money(Decimal("100000")),
            year=date.today().year + 1,
        )


def test_policy_limit(calculator, car, rules):
    deductible_percentage = Percentage(Decimal("0.10"))
    base_policy_limit = calculator.calculate_base_policy_limit(car=car, rules=rules)
    assert base_policy_limit.value == Decimal("100000")
    assert calculator.calculate_deductible_value(
        base_policy_limit=base_policy_limit,
        deductible_percentage=deductible_percentage,
    ).value == Decimal("10000")
    assert calculator.calculate_policy_limit(
        car=car, deductible_percentage=deductible_percentage, rules=rules
    ).value == Decimal("90000")


def test_premium(calculator, car):
    assert calculator.calculate_premium(
        applied_rate=Decimal("0.10"),
        broker_fee=Money(Decimal("50")),
        car=car,
        deductible_percentage=Percentage(Decimal("0.10")),
    ).value == Decimal("9050")


def test_value_rate(calculator, car, rules):
    assert calculator.calculate_value_rate(car=car, rules=rules) == Decimal("0.05")


def test_value_rate_counts_only_complete_blocks(calculator, rules):
    car = Car(
        make="Toyota",
        model="Corolla",
        value=Money(Decimal("99999")),
        year=2016,
    )
    value_rate = calculator.calculate_value_rate(car=car, rules=rules)
    assert value_rate == Decimal("0.045")
    assert value_rate / rules.value_rate_increment == Decimal("9")
