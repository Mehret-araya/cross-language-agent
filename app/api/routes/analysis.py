
from fastapi import APIRouter

from app.models import PackageInfo
from app.controllers.analysis_controller import (
    analyze_packages_controller,
)

router = APIRouter()


@router.post("/analyze")
def analyze_packages_endpoint(
    source: PackageInfo,
    target: PackageInfo,
) -> dict:
    return analyze_packages_controller(source, target)
