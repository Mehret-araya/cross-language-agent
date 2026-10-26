
from app.models import PackageInfo
from app.services.interoperability_service import (
    run_interoperability_workflow,
)


def analyze_packages_controller(
    source: PackageInfo,
    target: PackageInfo,
) -> dict:
    return run_interoperability_workflow(source, target)
