
from app.models import PackageInfo
from app.agents.analyzer import analyze_packages


def test_cross_language_packages_are_flagged():
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

    result = analyze_packages(source, target)

    assert result.compatible is False
    assert result.risks
    assert result.recommended_next_step


def test_unmatched_exports_add_specific_risk():
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

    result = analyze_packages(source, target)

    assert any(
        "No matching export names" in risk
        for risk in result.risks
    )


def test_matching_exports_do_not_establish_compatibility():
    source = PackageInfo(
        name="billing-python",
        language=" Python ",
        exports=[" calculate_total ", "calculate_total"],
    )
    target = PackageInfo(
        name="billing-python-port",
        language="python",
        exports=["calculate_total"],
    )

    result = analyze_packages(source, target)

    assert result.compatible is False
    assert "Exports with matching names: calculate_total" in result.evidence
    assert any(
        "do not prove API compatibility" in risk
        for risk in result.risks
    )


def test_empty_export_names_are_not_treated_as_documented():
    source = PackageInfo(
        name="billing-python",
        language="Python",
        exports=[],
    )
    target = PackageInfo(
        name="billing-python-port",
        language="Python",
        exports=["calculate_total"],
    )

    result = analyze_packages(source, target)

    assert any("Source package exports" in risk for risk in result.risks)
