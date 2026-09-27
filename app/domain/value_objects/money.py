from decimal import Decimal


class Money:
    def __init__(self, value: Decimal):
        if value < 0:
            raise ValueError("Money cannot be negative.")

        self._value = value

    @property
    def value(self) -> Decimal:
        return self._value