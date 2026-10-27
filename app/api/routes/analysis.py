
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import PackageInfo
from app.controllers.analysis_controller import (
    analyze_packages_controller,
)
from app.services.interoperability_service import (
    run_interoperability_workflow,
)
from app.integrations.java_bridge import (
    JavaBridgeError,
    JavaBridgeTimeout,
    JavaToolchainUnavailable,
    run_java_billing_example,
)

router = APIRouter()


def _raise_bridge_http_error(exc: JavaBridgeError) -> None:
    if isinstance(exc, JavaToolchainUnavailable):
        status_code = 503
    elif isinstance(exc, JavaBridgeTimeout):
        status_code = 504
    else:
        status_code = 502
    raise HTTPException(status_code=status_code, detail=str(exc)) from exc


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
    try:
        return run_java_billing_example(
            unit_price=request.unit_price,
            quantity=request.quantity,
        )
    except JavaBridgeError as exc:
        _raise_bridge_http_error(exc)


@router.post("/analyze-with-execution")
def analyze_with_execution(request: WorkflowRequest) -> dict:
    try:
        return run_interoperability_workflow(
            source=request.source,
            target=request.target,
            execute_example=request.execute_example,
        )
    except JavaBridgeError as exc:
        _raise_bridge_http_error(exc)
