from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.domain.value_objects.money import Money


class QuoteCalculated:
    def __init__(
        self,
        applied_rate: Decimal,
        calculated_premium: Money,
        policy_limit: Money,
        quote_id: UUID,
    ):
        self._applied_rate = applied_rate
        self._calculated_at = datetime.now(timezone.utc)
        self._calculated_premium = calculated_premium
        self._policy_limit = policy_limit
        self._quote_id = quote_id

    @property
    def applied_rate(self) -> Decimal:
        return self._applied_rate

    @property
    def calculated_at(self) -> datetime:
        return self._calculated_at

    @property
    def calculated_premium(self) -> Money:
        return self._calculated_premium

    @property
    def policy_limit(self) -> Money:
        return self._policy_limit

    @property
    def quote_id(self) -> UUID:
        return self._quote_id
