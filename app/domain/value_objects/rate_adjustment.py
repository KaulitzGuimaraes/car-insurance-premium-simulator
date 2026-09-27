from decimal import Decimal


class RateAdjustment:
    def __init__(
        self,
        maximum: Decimal,
        minimum: Decimal,
        value: Decimal,
    ):
        if not maximum.is_finite() or not minimum.is_finite() or minimum > maximum:
            raise ValueError("Rate adjustment limits must be finite and minimum <= maximum")

        if not value.is_finite() or value < minimum or value > maximum:
            raise ValueError(f"Rate adjustment must be between {minimum} and {maximum}")

        self._value = value

    @property
    def value(self) -> Decimal:
        return self._value
