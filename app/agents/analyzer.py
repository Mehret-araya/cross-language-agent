
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

    source_language = source.language.strip().casefold()
    target_language = target.language.strip().casefold()

    if source_language != target_language:
        risks.append(
            "Cross-language boundary needs an interoperability strategy."
        )

    source_exports = {name.strip() for name in source.exports if name.strip()}
    target_exports = {name.strip() for name in target.exports if name.strip()}

    if not source_exports:
        risks.append("Source package exports need documentation.")

    if not target_exports:
        risks.append("Target package exports need documentation.")

    if source_exports and target_exports:
        shared_exports = source_exports & target_exports
        if shared_exports:
            evidence.append(
                "Exports with matching names: "
                + ", ".join(sorted(shared_exports))
            )
            risks.append(
                "Matching export names do not prove API compatibility; "
                "verify signatures, data types, and behavior."
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
