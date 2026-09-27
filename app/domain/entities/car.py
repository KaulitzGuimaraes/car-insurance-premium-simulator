from datetime import date

from app.domain.value_objects.money import Money


class Car:
    def __init__(
        self,
        make: str,
        model: str,
        value: Money,
        year: int,
    ):
        if not make:
            raise ValueError("Make cannot be empty")

        if not model:
            raise ValueError("Model cannot be empty")

        if not isinstance(value, Money):
            raise ValueError("Value must be a Money instance")

        if year <= 0:
            raise ValueError("Year must be greater than zero")

        if year > date.today().year:
            raise ValueError("Year cannot be greater than current year")

        self._make = make
        self._model = model
        self._value = value
        self._year = year

    @property
    def make(self) -> str:
        return self._make

    @property
    def model(self) -> str:
        return self._model

    @property
    def value(self) -> Money:
        return self._value

    @property
    def year(self) -> int:
        return self._year