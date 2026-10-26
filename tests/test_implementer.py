
from app.models import PackageInfo
from app.agents.strategy import recommend_strategy
from app.agents.implementer import create_adapter_plan


def test_adapter_plan_contains_steps_and_tests():
    source = PackageInfo(
        name="billing-python",
        language="Python",
        exports=["calculate_total"],
    )
    target = PackageInfo(
        name="billing-java",
        language="Java",
        exports=["calculateTotal"],
    )

    strategy = recommend_strategy(source, target)
    plan = create_adapter_plan(source, target, strategy)

    assert plan.strategy == "rest_api"
    assert plan.steps
    assert plan.test_requirements
