
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import PackageInfo
from app.controllers.analysis_controller import (
    analyze_packages_controller,
)
from app.services.interoperability_service import (
    run_interoperability_workflow,
)
from app.integrations.java_bridge import run_java_billing_example

router = APIRouter()


class BillingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    unit_price: str = Field(min_length=1, max_length=32)
    quantity: int = Field(ge=0, strict=True)

    @field_validator("unit_price")
    @classmethod
    def validate_unit_price(cls, value: str) -> str:
        try:
            price = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError("Unit price must be a valid number.") from exc
        if not price.is_finite():
            raise ValueError("Unit price must be a finite number.")
        if price < 0:
            raise ValueError("Unit price cannot be negative.")
        return value


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: PackageInfo
    target: PackageInfo


class WorkflowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: PackageInfo
    target: PackageInfo
    execute_example: bool = False


@router.post("/analyze")
def analyze_packages_endpoint(request: AnalysisRequest) -> dict:
    return analyze_packages_controller(request.source, request.target)


@router.post("/execute-billing-example")
def execute_billing_example(request: BillingRequest) -> dict:
    return run_java_billing_example(
        unit_price=request.unit_price,
        quantity=request.quantity,
    )


@router.post("/analyze-with-execution")
def analyze_with_execution(request: WorkflowRequest) -> dict:
    return run_interoperability_workflow(
        source=request.source,
        target=request.target,
        execute_example=request.execute_example,
    )
