from decimal import Decimal

from app.domain.entities.car import Car
from app.domain.value_objects.money import Money
from app.domain.value_objects.percentage import Percentage
from app.domain.value_objects.pricing_rules import PricingRules
from app.domain.value_objects.rate_adjustment import RateAdjustment


class PremiumCalculator:
    def calculate_age_rate(
        self,
        car: Car,
        current_year: int,
        rules: PricingRules,
    ) -> Decimal:
        """
        Calculate the insurance rate derived from the car's age.

        The car age is calculated by subtracting the production year
        from the current year.

        Formula:
            car_age = current_year - car.year

            age_rate =
                car_age * age_rate_increment

        Example:
            current_year = 2026
            car.year = 2016
            age_rate_increment = 0.005

            car_age = 10
            age_rate = 10 * 0.005 = 0.05

            Result: 5%
        """
        car_age = current_year - car.year

        return Decimal(car_age) * rules.age_rate_increment

    def calculate_applied_rate(
        self,
        car: Car,
        current_year: int,
        geographic_adjustment: RateAdjustment | None,
        rules: PricingRules,
    ) -> Decimal:
        """
        Calculate the final rate applied to the insurance premium.

        The applied rate is the sum of:
        - the rate derived from the car's age;
        - the rate derived from the car's value;
        - the optional geographic risk adjustment.

        Formula:
            applied_rate =
                age_rate
                + value_rate
                + geographic_adjustment

        If no geographic adjustment is provided, its value is
        considered zero.

        Example:
            age_rate = 0.05
            value_rate = 0.05
            geographic_adjustment = 0.01

            applied_rate = 0.11

            Result: 11%
        """
        age_rate = self.calculate_age_rate(
            car=car,
            current_year=current_year,
            rules=rules,
        )

        value_rate = self.calculate_value_rate(
            car=car,
            rules=rules,
        )

        adjustment = geographic_adjustment.value if geographic_adjustment else Decimal("0")

        return age_rate + value_rate + adjustment

    def calculate_base_policy_limit(
        self,
        car: Car,
        rules: PricingRules,
    ) -> Money:
        """
        Calculate the policy limit before applying the deductible.

        Formula:
            base_policy_limit =
                car_value * coverage_percentage

        Example:
            car_value = 100000
            coverage_percentage = 1.00

            base_policy_limit = 100000
        """
        value = car.value.value * rules.coverage_percentage

        return Money(value)

    def calculate_base_premium(
        self,
        applied_rate: Decimal,
        car: Car,
    ) -> Money:
        """
        Calculate the premium before applying the deductible discount
        and broker fee.

        Formula:
            base_premium =
                car_value * applied_rate

        Example:
            car_value = 100000
            applied_rate = 0.10

            base_premium = 100000 * 0.10
            base_premium = 10000
        """
        value = car.value.value * applied_rate

        return Money(value)

    def calculate_deductible_discount(
        self,
        base_premium: Money,
        deductible_percentage: Percentage,
    ) -> Money:
        """
        Calculate the monetary discount applied to the base premium
        according to the selected deductible percentage.

        Formula:
            deductible_discount =
                base_premium * deductible_percentage

        Example:
            base_premium = 10000
            deductible_percentage = 0.10

            deductible_discount = 10000 * 0.10
            deductible_discount = 1000
        """
        value = base_premium.value * deductible_percentage.value

        return Money(value)

    def calculate_deductible_value(
        self,
        base_policy_limit: Money,
        deductible_percentage: Percentage,
    ) -> Money:
        """
        Calculate the monetary value of the deductible based on the
        original policy limit.

        Formula:
            deductible_value =
                base_policy_limit * deductible_percentage

        Example:
            base_policy_limit = 100000
            deductible_percentage = 0.10

            deductible_value = 100000 * 0.10
            deductible_value = 10000
        """
        value = base_policy_limit.value * deductible_percentage.value

        return Money(value)

    def calculate_policy_limit(
        self,
        car: Car,
        deductible_percentage: Percentage,
        rules: PricingRules,
    ) -> Money:
        """
        Calculate the final insurance policy limit after applying
        the deductible.

        First, the base policy limit is calculated using the car
        value and the configured coverage percentage.

        Formula:
            base_policy_limit =
                car_value * coverage_percentage

            deductible_value =
                base_policy_limit * deductible_percentage

            policy_limit =
                base_policy_limit - deductible_value

        Example:
            car_value = 100000
            coverage_percentage = 1.00
            deductible_percentage = 0.10

            base_policy_limit = 100000
            deductible_value = 10000
            policy_limit = 90000
        """
        base_policy_limit = Money(car.value.value * rules.coverage_percentage)

        deductible_value = self.calculate_deductible_value(
            base_policy_limit=base_policy_limit,
            deductible_percentage=deductible_percentage,
        )

        value = base_policy_limit.value - deductible_value.value

        return Money(value)

    def calculate_premium(
        self,
        applied_rate: Decimal,
        broker_fee: Money,
        car: Car,
        deductible_percentage: Percentage,
    ) -> Money:
        """
        Calculate the final insurance premium.

        First, the base premium is calculated from the car value
        and applied rate.

        Then, the deductible discount is subtracted from the base
        premium.

        Finally, the broker fee is added.

        Formula:
            base_premium =
                car_value * applied_rate

            deductible_discount =
                base_premium * deductible_percentage

            final_premium =
                base_premium
                - deductible_discount
                + broker_fee

        Example:
            car_value = 100000
            applied_rate = 0.10
            deductible_percentage = 0.10
            broker_fee = 50

            base_premium = 10000
            deductible_discount = 1000
            final_premium = 9050
        """
        base_premium = self.calculate_base_premium(
            applied_rate=applied_rate,
            car=car,
        )

        deductible_discount = self.calculate_deductible_discount(
            base_premium=base_premium,
            deductible_percentage=deductible_percentage,
        )

        value = base_premium.value - deductible_discount.value + broker_fee.value

        return Money(value)

    def calculate_value_rate(
        self,
        car: Car,
        rules: PricingRules,
    ) -> Decimal:
        """
        Calculate the insurance rate derived from the car's value.

        The rate increases once for every complete configured value
        block.

        Formula:
            value_blocks =
                car_value // value_rate_step

            value_rate =
                value_blocks * value_rate_increment

        Example:
            car_value = 100000
            value_rate_step = 10000
            value_rate_increment = 0.005

            value_blocks = 10
            value_rate = 10 * 0.005
            value_rate = 0.05

            Result: 5%

        Only complete value blocks are considered. For example,
        a car valued at 99999 with a value step of 10000 produces
        9 complete blocks.
        """
        value_blocks = car.value.value // rules.value_rate_step

        return value_blocks * rules.value_rate_increment
