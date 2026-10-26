
from dataclasses import dataclass

from app.models import PackageInfo
from app.agents.strategy import StrategyResult


@dataclass
class AdapterPlan:
    source_package: str
    target_package: str
    strategy: str
    steps: list[str]
    test_requirements: list[str]


def create_adapter_plan(
    source: PackageInfo,
    target: PackageInfo,
    strategy: StrategyResult,
) -> AdapterPlan:
    return AdapterPlan(
        source_package=source.name,
        target_package=target.name,
        strategy=strategy.strategy,
        steps=[
            f"Inspect the public API of {source.name}.",
            f"Define the interface required by {target.name}.",
            f"Implement the adapter using the {strategy.strategy} strategy.",
            "Document data conversions and error handling.",
        ],
        test_requirements=[
            "Test successful calls and expected return values.",
            "Test invalid inputs and error handling.",
            "Verify data types across the language boundary.",
        ],
    )
