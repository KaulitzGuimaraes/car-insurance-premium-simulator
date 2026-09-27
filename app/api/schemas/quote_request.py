from pydantic import BaseModel, Field


class AddressRequest(BaseModel):
    city: str
    country: str
    state: str


class QuoteRequest(BaseModel):
    broker_fee: float = Field(ge=0)
    deductible_percentage: float = Field(ge=0, le=1)
    make: str = Field(min_length=1)
    model: str = Field(min_length=1)
    registration_location: AddressRequest | None = None
    value: float = Field(gt=0)
    year: int = Field(gt=0)
