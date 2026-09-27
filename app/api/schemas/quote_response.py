from pydantic import BaseModel


class CarResponse(BaseModel):
    make: str
    model: str
    value: float
    year: int


class QuoteResponse(BaseModel):
    applied_rate: float
    calculated_premium: float
    car: CarResponse
    deductible_value: float
    policy_limit: float
