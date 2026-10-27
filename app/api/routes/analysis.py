
from fastapi import APIRouter
from pydantic import BaseModel, Field

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
    unit_price: str = Field(min_length=1)
    quantity: int

class WorkflowRequest(BaseModel):
    source: PackageInfo
    target: PackageInfo
    execute_example: bool = False


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


@router.post("/analyze-with-execution")
def analyze_with_execution(request: WorkflowRequest) -> dict:
    return run_interoperability_workflow(
        source=request.source,
        target=request.target,
        execute_example=request.execute_example,
    )
