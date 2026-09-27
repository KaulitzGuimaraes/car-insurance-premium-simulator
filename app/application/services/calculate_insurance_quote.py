from datetime import date

from app.domain.aggregates.insurance_quote import InsuranceQuote
from app.domain.entities.car import Car
from app.domain.events.quote_calculated import QuoteCalculated
from app.domain.services.premium_calculator import PremiumCalculator
from app.domain.value_objects.money import Money
from app.domain.value_objects.percentage import Percentage
from app.domain.value_objects.pricing_rules import PricingRules
from app.domain.value_objects.rate_adjustment import RateAdjustment


class CalculateInsuranceQuoteService:
    def __init__(
        self,
        calculator: PremiumCalculator,
    ):
        self._calculator = calculator

    def calculate(
        self,
        broker_fee: Money,
        car: Car,
        deductible_percentage: Percentage,
        geographic_adjustment: RateAdjustment | None,
        pricing_rules: PricingRules,
    ) -> tuple[InsuranceQuote, QuoteCalculated]:
        """
        Coordinate the insurance quote calculation.

        This application service does not implement business formulas.
        It delegates all calculations to the PremiumCalculator domain
        service and uses the results to create the InsuranceQuote
        aggregate and QuoteCalculated domain event.

        Flow:
            1. Calculate the applied insurance rate.
            2. Calculate the base policy limit.
            3. Calculate the deductible monetary value.
            4. Calculate the final policy limit.
            5. Calculate the final premium.
            6. Create the InsuranceQuote aggregate.
            7. Create the QuoteCalculated domain event.
        """

        applied_rate = self._calculator.calculate_applied_rate(
            car=car,
            current_year=date.today().year,
            geographic_adjustment=geographic_adjustment,
            rules=pricing_rules,
        )

        base_policy_limit = self._calculator.calculate_base_policy_limit(
            car=car,
            rules=pricing_rules,
        )

        deductible_value = self._calculator.calculate_deductible_value(
            base_policy_limit=base_policy_limit,
            deductible_percentage=deductible_percentage,
        )

        policy_limit = self._calculator.calculate_policy_limit(
            car=car,
            deductible_percentage=deductible_percentage,
            rules=pricing_rules,
        )

        calculated_premium = self._calculator.calculate_premium(
            applied_rate=applied_rate,
            broker_fee=broker_fee,
            car=car,
            deductible_percentage=deductible_percentage,
        )

        quote = InsuranceQuote(
            applied_rate=applied_rate,
            broker_fee=broker_fee,
            calculated_premium=calculated_premium,
            car=car,
            deductible_percentage=deductible_percentage,
            deductible_value=deductible_value,
            policy_limit=policy_limit,
        )

        event = QuoteCalculated(
            applied_rate=quote.applied_rate,
            calculated_premium=quote.calculated_premium,
            policy_limit=quote.policy_limit,
            quote_id=quote.quote_id,
        )

        return quote, event
