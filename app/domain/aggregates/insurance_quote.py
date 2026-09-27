from decimal import Decimal
from uuid import UUID, uuid4

from app.domain.entities.car import Car
from app.domain.value_objects.money import Money
from app.domain.value_objects.percentage import Percentage


class InsuranceQuote:
    def __init__(
        self,
        applied_rate: Decimal,
        broker_fee: Money,
        calculated_premium: Money,
        car: Car,
        deductible_percentage: Percentage,
        deductible_value: Money,
        policy_limit: Money,
        quote_id: UUID | None = None,
    ):
        self._applied_rate = applied_rate
        self._broker_fee = broker_fee
        self._calculated_premium = calculated_premium
        self._car = car
        self._deductible_percentage = deductible_percentage
        self._deductible_value = deductible_value
        self._policy_limit = policy_limit
        self._quote_id = quote_id or uuid4()

    @property
    def applied_rate(self) -> Decimal:
        return self._applied_rate

    @property
    def broker_fee(self) -> Money:
        return self._broker_fee

    @property
    def calculated_premium(self) -> Money:
        return self._calculated_premium

    @property
    def car(self) -> Car:
        return self._car

    @property
    def deductible_percentage(self) -> Percentage:
        return self._deductible_percentage

    @property
    def deductible_value(self) -> Money:
        return self._deductible_value

    @property
    def policy_limit(self) -> Money:
        return self._policy_limit

    @property
    def quote_id(self) -> UUID:
        return self._quote_id

