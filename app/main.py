from fastapi import FastAPI

from app.api.router import api_router
from app.application.services.calculate_insurance_quote import CalculateInsuranceQuoteService
from app.domain.services.premium_calculator import PremiumCalculator
from app.infrastructure.config.settings import DEFAULT_CONFIG_PATH, load_settings


def create_app(config_path: str = str(DEFAULT_CONFIG_PATH)) -> FastAPI:
    business_settings = load_settings(config_path=config_path)
    application = FastAPI(
        title="Car Insurance Premium Simulator",
        version="0.1.0",
    )
    application.state.business_settings = business_settings
    application.state.calculate_insurance_quote = CalculateInsuranceQuoteService(
        calculator=PremiumCalculator(),
    )
    application.include_router(api_router, prefix="/api/v1")
    return application


app = create_app()
