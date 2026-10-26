
from app.models import PackageInfo, AnalysisResult


def analyze_packages(
    source: PackageInfo,
    target: PackageInfo,
) -> AnalysisResult:
    risks = []

    evidence = [
        f"Source: {source.name} ({source.language})",
        f"Target: {target.name} ({target.language})",
    ]

    if source.language.lower() != target.language.lower():
        risks.append(
            "Cross-language boundary needs an interoperability strategy."
        )

    if not source.exports:
        risks.append("Source package exports need documentation.")

    if not target.exports:
        risks.append("Target package exports need documentation.")

    return AnalysisResult(
        compatible=not risks,
        risks=risks,
        evidence=evidence,
        recommended_next_step=(
            "Inspect APIs and choose an adapter strategy."
            if risks
            else "Run compatibility tests."
        ),
    )
