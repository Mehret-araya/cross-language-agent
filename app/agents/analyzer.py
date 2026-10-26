
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

    source_language = source.language.strip().lower()
    target_language = target.language.strip().lower()

    if source_language != target_language:
        risks.append(
            "Cross-language boundary needs an interoperability strategy."
        )

    if not source.exports:
        risks.append("Source package exports need documentation.")

    if not target.exports:
        risks.append("Target package exports need documentation.")

    if source.exports and target.exports:
        source_exports = {name.strip() for name in source.exports}
        target_exports = {name.strip() for name in target.exports}
        shared_exports = source_exports & target_exports

        if shared_exports:
            evidence.append(
                "Exports with matching names: "
                + ", ".join(sorted(shared_exports))
            )
        else:
            risks.append(
                "No matching export names found; map the APIs explicitly."
            )

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
