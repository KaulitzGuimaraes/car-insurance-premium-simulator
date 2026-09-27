# Car Insurance Premium Simulator

Backend service for calculating car insurance premiums based on vehicle age, vehicle value, deductible percentage, broker fee, and configurable pricing rules.

The project is implemented with **FastAPI**, follows **DDD**, **SOLID**, and **Clean Architecture** principles, and is prepared for containerized execution with Docker.

## Main Features

- Dynamic insurance rate calculation based on:
  - vehicle age
  - vehicle value
- Deductible discount calculation
- Final premium calculation
- Policy limit calculation
- Configurable pricing rules through YAML
- Clear separation between domain, application, API, and infrastructure layers
- Domain concepts modeled with:
  - Value Objects
  - Entities
  - Aggregate Root
  - Domain Service
  - Domain Event
- Optional GIS adjustment prepared through `registration_location`

## Architecture

The project is organized into four main layers:

```text
app/
├── api/
├── application/
├── domain/
├── infrastructure/
└── main.py
```

### Domain

Contains the core business rules and models.

Main concepts:

- `Money`
- `Percentage`
- `RateAdjustment`
- `Address`
- `Car`
- `PricingRules`
- `PremiumCalculator`
- `InsuranceQuote`
- `QuoteCalculated`

The domain does not depend on FastAPI, YAML, Docker, or external infrastructure.

### Application

Contains application services responsible for coordinating domain operations.

Example:

```text
CalculateInsuranceQuoteService
```

It delegates calculation logic to the domain and creates the final quote result.

### API

Contains FastAPI routes and request/response schemas.

Main endpoint:

```text
POST /api/v1/quotes
```

### Infrastructure

Contains technical implementations such as configuration loading and future external integrations.

Pricing rules are loaded from:

```text
config.yaml
```

## Pricing Rules

Default configuration:

```yaml
gis:
  max_adjustment: 0.02
  min_adjustment: -0.02

pricing:
  age_rate_increment: 0.005
  coverage_percentage: 1.0
  value_rate_increment: 0.005
  value_rate_step: 10000
```

### Applied Rate

```text
age_rate =
    car_age * age_rate_increment

value_rate =
    complete_value_blocks * value_rate_increment

applied_rate =
    age_rate + value_rate + geographic_adjustment
```

### Premium

```text
base_premium =
    car_value * applied_rate

deductible_discount =
    base_premium * deductible_percentage

calculated_premium =
    base_premium
    - deductible_discount
    + broker_fee
```

### Policy Limit

```text
base_policy_limit =
    car_value * coverage_percentage

deductible_value =
    base_policy_limit * deductible_percentage

policy_limit =
    base_policy_limit - deductible_value
```

## Running the Application

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app.main:app --reload
```

The Swagger documentation will be available at:

```text
http://localhost:8000/docs
```

## Example Request

```json
{
  "broker_fee": 50,
  "deductible_percentage": 0.10,
  "make": "Toyota",
  "model": "Corolla",
  "registration_location": null,
  "value": 100000,
  "year": 2016
}
```

## Testing

Run the test suite with:

```bash
pytest
```

The test strategy includes domain validation, configuration behavior, and API integration.

## Design Decisions

- `Decimal` is used internally for monetary calculations to avoid floating-point precision issues.
- Complete vehicle-value blocks are used when calculating the value-based rate.
- Configurable business rules are loaded from YAML instead of being hard-coded.
- FastAPI is kept outside the domain layer.
- `QuoteCalculated` represents the domain event generated after a successful quote calculation.
- The GIS adjustment is optional. The domain is already prepared to receive a geographic risk adjustment through `RateAdjustment`, so a concrete GIS provider can be added later without changing the core premium calculation logic.