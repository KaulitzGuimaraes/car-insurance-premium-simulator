from decimal import Decimal

from fastapi import APIRouter, HTTPException, Request, status

from app.api.schemas.quote_request import QuoteRequest
from app.api.schemas.quote_response import CarResponse, QuoteResponse
from app.domain.entities.car import Car
from app.domain.value_objects.money import Money
from app.domain.value_objects.percentage import Percentage

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post("", response_model=QuoteResponse, status_code=status.HTTP_200_OK)
def calculate_quote(
    payload: QuoteRequest,
    request: Request,
) -> QuoteResponse:
    try:
        car = Car(
            make=payload.make,
            model=payload.model,
            value=Money(Decimal(str(payload.value))),
            year=payload.year,
        )
        broker_fee = Money(Decimal(str(payload.broker_fee)))
        deductible_percentage = Percentage(Decimal(str(payload.deductible_percentage)))

        quote, _event = request.app.state.calculate_insurance_quote.calculate(
            broker_fee=broker_fee,
            car=car,
            deductible_percentage=deductible_percentage,
            geographic_adjustment=None,
            pricing_rules=request.app.state.business_settings.to_pricing_rules(),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return QuoteResponse(
        applied_rate=float(quote.applied_rate),
        calculated_premium=float(quote.calculated_premium.value),
        car=CarResponse(
            make=quote.car.make,
            model=quote.car.model,
            value=float(quote.car.value.value),
            year=quote.car.year,
        ),
        deductible_value=float(quote.deductible_value.value),
        policy_limit=float(quote.policy_limit.value),
    )
