
from fastapi import APIRouter
from pydantic import BaseModel

from app.models import PackageInfo
from app.controllers.analysis_controller import (
    analyze_packages_controller,
)
from app.integrations.java_bridge import run_java_billing_example

router = APIRouter()


class BillingRequest(BaseModel):
    unit_price: str
    quantity: int


@router.post("/analyze")
def analyze_packages_endpoint(
    source: PackageInfo,
    target: PackageInfo,
) -> dict:
    return analyze_packages_controller(source, target)


@router.post("/execute-billing-example")
def execute_billing_example(request: BillingRequest) -> dict:
    return run_java_billing_example(
        unit_price=request.unit_price,
        quantity=request.quantity,
    )
