from decimal import Decimal


class PricingRules:
    def __init__(
        self,
        age_rate_increment: Decimal,
        coverage_percentage: Decimal,
        value_rate_increment: Decimal,
        value_rate_step: Decimal,
    ):
        if age_rate_increment <= 0:
            raise ValueError("Age rate increment must be greater than zero")

        if coverage_percentage < 0 or coverage_percentage > 1:
            raise ValueError("Coverage percentage must be between 0 and 1")

        if value_rate_increment <= 0:
            raise ValueError("Value rate increment must be greater than zero")

        if value_rate_step <= 0:
            raise ValueError("Value rate step must be greater than zero")

        self._age_rate_increment = age_rate_increment
        self._coverage_percentage = coverage_percentage
        self._value_rate_increment = value_rate_increment
        self._value_rate_step = value_rate_step

    @property
    def age_rate_increment(self) -> Decimal:
        return self._age_rate_increment

    @property
    def coverage_percentage(self) -> Decimal:
        return self._coverage_percentage

    @property
    def value_rate_increment(self) -> Decimal:
        return self._value_rate_increment

    @property
    def value_rate_step(self) -> Decimal:
        return self._value_rate_step
