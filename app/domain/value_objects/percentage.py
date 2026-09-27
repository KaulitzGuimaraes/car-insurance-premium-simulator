from decimal import Decimal

class Percentage:
    def __init__(self, value: Decimal):
        if value <0 or value > 1:
            raise ValueError("Percentage must be between 0 and 1")
        self._value = value

    @property
    def value(self) -> Decimal:
        return self._value
