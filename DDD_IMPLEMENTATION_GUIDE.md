# DDD Implementation Guide — Car Insurance Premium Simulator

This document describes how the assessment can be implemented using **Domain-Driven Design (DDD)**, **SOLID**, **Clean Architecture**, and a thin **FastAPI** interface.

The goal is not to overengineer the solution. The idea is to make the business rules explicit, keep the domain independent from frameworks, and clearly distinguish between **Value Objects, Entities, Aggregates, Domain Services, and Domain Events**.

---

## 1. Define the Business Rules First

Before writing framework code, define the domain rules clearly.

### Car Age

The car age is calculated using the current year minus the production year.

```text
car_age = current_year - car_year
```

### Age-Based Rate

For every year since the car was produced, add a configurable percentage to the insurance rate.

```text
age_rate = car_age * age_rate_increment
```

Default:

```text
age_rate_increment = 0.005
```

### Value-Based Rate

For every complete configurable value block, add another configurable percentage.

```text
value_blocks = car_value // value_rate_step
value_rate = value_blocks * value_rate_increment
```

Default values:

```text
value_rate_step = 10000
value_rate_increment = 0.005
```

### Applied Rate

```text
applied_rate = age_rate + value_rate
```

### Base Premium

```text
base_premium = car_value * applied_rate
```

### Deductible Discount

```text
deductible_discount = base_premium * deductible_percentage
```

### Final Premium

```text
calculated_premium = base_premium - deductible_discount + broker_fee
```

### Base Policy Limit

```text
base_policy_limit = car_value * coverage_percentage
```

Default:

```text
coverage_percentage = 1.0
```

### Deductible Value

```text
deductible_value = base_policy_limit * deductible_percentage
```

### Final Policy Limit

```text
policy_limit = base_policy_limit - deductible_value
```

---

## 2. Identify the Main Bounded Context

For this assessment, the main **Bounded Context** can be:

```text
Insurance Quoting
```

Its responsibility is to calculate an insurance quote from vehicle data and insurance parameters.

Concepts inside this context include:

```text
Car
InsuranceQuote
Premium
Deductible
PolicyLimit
AppliedRate
PremiumCalculator
```

The optional GIS feature can be modeled as a separate concern or external context:

```text
Insurance Quoting
        |
        v
Geographic Risk
```

The insurance domain does not need to know how geographic risk is calculated. It only needs a risk adjustment value.

---

## 3. Define the Ubiquitous Language

Use the same business terminology in:

- code
- tests
- documentation
- API contracts
- technical discussions

Suggested vocabulary:

```text
Car
Insurance Quote
Premium
Base Premium
Deductible
Deductible Value
Policy Limit
Applied Rate
Broker Fee
Coverage Percentage
Geographic Risk Adjustment
```

Avoid vague names such as:

```text
DataObject
Item
Processor
GenericService
```

when a specific domain concept exists.

---

## 4. Create the Value Objects

Value Objects represent concepts identified by their values rather than by a unique identity.

They should also protect domain invariants.

### Money

Represents monetary values.

Recommended internal type:

```python
Decimal
```

Validation:

```text
Money cannot be negative.
```

Benefits:

- centralizes financial validation
- avoids raw floats inside the domain
- helps prevent floating-point precision problems
- makes domain intent clearer

### Percentage

Represents percentages such as:

```text
deductible percentage
coverage percentage
applied rate
```

For standard percentages:

```text
0 <= value <= 1
```

### RateAdjustment

Recommended for the optional GIS feature.

A separate value object is cleaner than weakening the normal `Percentage` rules.

Suggested range:

```text
-0.02 <= value <= 0.02
```

### Address

Used only if the optional GIS requirement is implemented.

Possible fields:

```text
city
country
postal_code
state
street
```

It is a Value Object because its meaning comes from its values, not from an identity.

---

## 5. Create the Main Entity

### Car

`Car` can be modeled as a domain Entity.

Suggested attributes:

```text
make
model
year
value
```

Possible domain validations:

```text
make must not be empty
model must not be empty
year must not be in the future
value must be valid Money
```

The Entity should not depend on FastAPI or Pydantic.

---

## 6. Create the Aggregate

### InsuranceQuote

`InsuranceQuote` can be used as the Aggregate Root for the quote calculation.

Possible state:

```text
car
applied_rate
broker_fee
calculated_premium
deductible_percentage
deductible_value
policy_limit
```

Conceptually:

```text
InsuranceQuote
|
+-- Car
+-- AppliedRate
+-- Deductible
+-- BrokerFee
+-- Premium
+-- PolicyLimit
```

The Aggregate keeps the quote state consistent as one domain concept.

---

## 7. Create the Domain Service

### PremiumCalculator

The premium calculation does not naturally belong only to `Car` or only to `InsuranceQuote`.

For that reason, it can be modeled as a **Domain Service**.

Possible responsibilities:

```text
calculate_applied_rate
calculate_policy_limit
calculate_premium
```

Important rule:

```text
FastAPI controllers must not contain premium calculation logic.
```

Preferred flow:

```text
Controller
    |
    v
Use Case
    |
    v
PremiumCalculator
```

---

## 8. Create the Application Use Case

Create an application service/use case such as:

```text
CalculateInsuranceQuote
```

Its responsibility is orchestration, not domain calculation.

Suggested flow:

```text
Request
  |
  v
Create domain objects
  |
  v
Call PremiumCalculator
  |
  v
Create InsuranceQuote
  |
  v
Create Domain Event
  |
  v
Return result
```

---

## 9. Add the Domain Event

The assessment explicitly asks for events.

Suggested event:

```text
QuoteCalculated
```

Possible fields:

```text
applied_rate
calculated_at
calculated_premium
policy_limit
quote_id
```

The event represents something that already happened in the domain.

A production system could later publish it to Kafka, RabbitMQ, SNS/SQS, analytics, auditing, or other downstream consumers.

A real message broker is not required unless explicitly requested.

---

## 10. Keep FastAPI in the Presentation Layer

FastAPI should be treated as an external delivery mechanism.

Its responsibilities are:

```text
receive HTTP request
validate API input
map request to application input
call the use case
map domain result to response
return HTTP response
```

Suggested flow:

```text
POST /quotes
    |
    v
FastAPI Controller
    |
    v
CalculateInsuranceQuote
    |
    v
Domain
```

The domain should not import FastAPI, `APIRouter`, Pydantic `BaseModel`, `Request`, or `Response`.

---

## 11. Separate API Schemas From Domain Models

Use Pydantic for external API contracts.

Example:

```text
presentation/
    schemas/
        quote_request.py
        quote_response.py
```

Keep pure Python domain objects separately:

```text
domain/
    entities/
    value_objects/
    aggregates/
```

---

## 12. Use Configuration Instead of Magic Numbers

The challenge explicitly requires configurable values.

Suggested environment variables:

```env
AGE_RATE_INCREMENT=0.005
DEFAULT_COVERAGE_PERCENTAGE=1.0
GIS_MAX_ADJUSTMENT=0.02
GIS_MIN_ADJUSTMENT=-0.02
VALUE_RATE_INCREMENT=0.005
VALUE_RATE_STEP=10000
```

Do not hard-code these values throughout the domain.

---

## 13. Implement the Optional GIS Feature Using Dependency Inversion

Do not couple the domain directly to a concrete GIS API.

Create an abstraction such as:

```text
GeographicRiskProvider
```

Conceptual contract:

```python
class GeographicRiskProvider(Protocol):
    def get_risk_adjustment(self, address: Address) -> RateAdjustment:
        ...
```

Then create an infrastructure implementation:

```text
MockGeographicRiskProvider
ExternalGeographicRiskProvider
```

Architecture:

```text
Domain/Application
       |
       v
GeographicRiskProvider
       ^
       |
Infrastructure implementation
```

This demonstrates the SOLID **Dependency Inversion Principle**.

---

## 14. Apply the GIS Adjustment

If a registration location is provided:

```text
base_rate = age_rate + value_rate
```

Then:

```text
applied_rate = base_rate + geographic_risk_adjustment
```

Suggested default range:

```text
-2% to +2%
```

If no location is provided:

```text
geographic_risk_adjustment = 0
```

---

## 15. Suggested Clean Architecture Structure

```text
app/
|
+-- application/
|   +-- use_cases/
|       +-- calculate_insurance_quote.py
|
+-- domain/
|   +-- aggregates/
|   |   +-- insurance_quote.py
|   |
|   +-- entities/
|   |   +-- car.py
|   |
|   +-- events/
|   |   +-- quote_calculated.py
|   |
|   +-- services/
|   |   +-- premium_calculator.py
|   |
|   +-- value_objects/
|       +-- address.py
|       +-- money.py
|       +-- percentage.py
|       +-- rate_adjustment.py
|
+-- infrastructure/
|   +-- config/
|   |   +-- settings.py
|   |
|   +-- gis/
|       +-- geographic_risk_provider.py
|       +-- mock_geographic_risk_provider.py
|
+-- presentation/
|   +-- controllers/
|   |   +-- quote_controller.py
|   |
|   +-- schemas/
|       +-- quote_request.py
|       +-- quote_response.py
|
+-- main.py
```

DDD does **not** require a specific folder structure.

The important rule is dependency direction:

```text
Presentation
     |
     v
Application
     |
     v
Domain
```

Infrastructure implements technical details required by the application/domain.

---

## 16. MVC and DDD Can Coexist

MVC and DDD solve different problems.

MVC helps organize interface responsibilities.

DDD focuses on modeling business concepts and rules.

For this assessment:

```text
Controller
    |
    v
Application Use Case
    |
    v
Domain Model
```

FastAPI acts mainly as the Controller/API delivery layer.

DDD remains responsible for the business domain.

---

## 17. Unit Testing Strategy

Start by testing the domain independently from FastAPI.

Recommended cases:

### Rate Calculation

```text
10-year-old car
value = 100000

Expected:
age rate = 5%
value rate = 5%
applied rate = 10%
```

### Deductible

Verify the deductible discount is correctly applied.

### Broker Fee

Verify the broker fee is added after the deductible discount.

### Policy Limit

Verify the base policy limit, deductible value, and final policy limit.

### Invalid Car Year

A future production year should fail.

### Invalid Money

Negative money should fail.

### Invalid Percentage

Values below 0 or above 1 should fail for standard percentages.

### Custom Configuration

Verify that changing configuration changes the result without changing domain code.

### GIS Positive Adjustment

Example:

```text
+2%
```

should increase the applied rate correctly.

### GIS Negative Adjustment

Example:

```text
-2%
```

should decrease the applied rate correctly.

### No Registration Location

The calculation should work normally without GIS.

### GIS Limits

The risk adjustment must never exceed the configured minimum or maximum.

---

## 18. Integration Testing Strategy

After domain tests pass, test the FastAPI layer.

At minimum:

```text
POST /quotes
```

Verify:

```text
HTTP status
request validation
response structure
calculation result
```

---

## 19. Domain Decisions Worth Explaining in the README

Document important assumptions.

### Complete Value Blocks

The requirement says:

```text
For every $10,000 of the car's value
```

A reasonable interpretation is to use complete blocks:

```text
99999 -> 9 blocks
100000 -> 10 blocks
```

Document this decision explicitly.

### Current Year

Document how car age is calculated and how the current year is obtained.

### Decimal

Explain why `Decimal` is used internally for financial values.

### GIS

Explain that the GIS integration uses an abstraction so the provider can be replaced without changing domain logic.

### Events

Explain that `QuoteCalculated` is modeled as a domain event and could later be published to a message broker.

---

## 20. SOLID Mapping

### Single Responsibility Principle

Each class should have one primary responsibility.

```text
Car -> vehicle domain data
Money -> monetary validation
PremiumCalculator -> insurance calculation
QuoteController -> HTTP interface
```

### Open/Closed Principle

The GIS provider can be replaced or extended without modifying the core calculation flow.

### Liskov Substitution Principle

Different implementations of `GeographicRiskProvider` should be interchangeable.

### Interface Segregation Principle

Keep external provider interfaces small and focused.

### Dependency Inversion Principle

High-level business logic should depend on abstractions rather than concrete GIS implementations.

---

## 21. Final Implementation Order

```text
1. Business rules
2. Value Objects
3. Car Entity
4. PremiumCalculator Domain Service
5. InsuranceQuote Aggregate
6. QuoteCalculated Domain Event
7. CalculateInsuranceQuote Use Case
8. Configuration
9. FastAPI schemas
10. FastAPI controller
11. Optional GIS abstraction
12. GIS implementation
13. Unit tests
14. Integration tests
15. Docker
16. README documentation
```

---

## 22. Final Architecture Summary

```text
Client
  |
  v
FastAPI
Presentation Layer
  |
  v
CalculateInsuranceQuote
Application Layer
  |
  v
Insurance Quoting Domain
  |
  +-- Car
  +-- InsuranceQuote
  +-- Money
  +-- Percentage
  +-- PremiumCalculator
  +-- QuoteCalculated
  |
  v
GeographicRiskProvider
  |
  v
Infrastructure / GIS
```

Core principle:

> The business domain should remain independent from FastAPI, Docker, GIS providers, and other infrastructure concerns.

Frameworks should support the domain, not define it.
