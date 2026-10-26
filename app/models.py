from dataclasses import dataclass, field


@dataclass
class PackageInfo:
    name: str
    language: str
    version: str = ""
    runtime: str = ""
    exports: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    compatible: bool
    risks: list[str]
    evidence: list[str]
    recommended_next_step: str