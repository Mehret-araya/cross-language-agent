
from app.models import PackageInfo
from app.agents.strategy import recommend_strategy


def test_recommends_rest_api_for_different_languages():
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

    result = recommend_strategy(source, target)

    assert result.strategy == "rest_api"
    assert result.next_steps
