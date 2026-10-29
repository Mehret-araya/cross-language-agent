
import json

from app.integrations.json_adapter import handle_json_request
from app.integrations.java_bridge import run_java_billing_example
from app.models import PackageInfo
from app.agents.analyzer import analyze_packages
from app.agents.strategy import recommend_strategy
from app.agents.implementer import create_adapter_plan


def run_adapter_example(a: int, b: int) -> dict:
    """Demonstrate a function call through the JSON adapter."""

    def add(x: int, y: int) -> int:
        return x + y

    request = json.dumps({"arguments": {"x": a, "y": b}})
    response = handle_json_request(request, add)
    return json.loads(response)


def run_interoperability_workflow(
    source: PackageInfo,
    target: PackageInfo,
    execute_example: bool = False,
    unit_price: str | None = None,
    quantity: int | None = None,
) -> dict:
    analysis = analyze_packages(source, target)
    strategy = recommend_strategy(source, target)
    plan = create_adapter_plan(source, target, strategy)

    result = {
        "analysis": {
            "compatible": analysis.compatible,
            "risks": analysis.risks,
            "evidence": analysis.evidence,
            "recommended_next_step": analysis.recommended_next_step,
        },
        "strategy": {
            "name": strategy.strategy,
            "reason": strategy.reason,
            "next_steps": strategy.next_steps,
        },
        "adapter_plan": {
            "source_package": plan.source_package,
            "target_package": plan.target_package,
            "strategy": plan.strategy,
            "steps": plan.steps,
            "test_requirements": plan.test_requirements,
        },
    }

    if execute_example:
        if unit_price is None or quantity is None:
            raise ValueError(
                "Unit price and quantity are required to execute billing."
            )
        result["execution_example"] = run_java_billing_example(
            unit_price=unit_price,
            quantity=quantity,
        )

    return result
