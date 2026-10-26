
from dataclasses import dataclass

from app.models import PackageInfo


@dataclass
class StrategyResult:
    strategy: str
    reason: str
    next_steps: list[str]


def recommend_strategy(
    source: PackageInfo,
    target: PackageInfo,
) -> StrategyResult:
    source_language = source.language.lower()
    target_language = target.language.lower()

    if source_language == target_language:
        return StrategyResult(
            strategy="direct_import",
            reason="Both packages use the same programming language.",
            next_steps=[
                "Check package versions and dependencies.",
                "Run API compatibility tests.",
            ],
        )

    return StrategyResult(
        strategy="rest_api",
        reason=(
            "A language-neutral HTTP interface can connect packages "
            "written in different languages."
        ),
        next_steps=[
            "Identify the functions that need to be exposed.",
            "Define request and response schemas.",
            "Implement an HTTP adapter.",
            "Add integration tests for errors and data types.",
        ],
    )
