from pydantic import BaseModel, ConfigDict, Field, field_validator


class PackageInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=128)
    language: str = Field(min_length=1, max_length=64)
    version: str = Field(default="", max_length=128)
    runtime: str = Field(default="", max_length=128)
    exports: list[str] = Field(default_factory=list, max_length=100)


    @field_validator("name", "language", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return value.strip()

    @field_validator("exports")
    @classmethod
    def normalize_exports(cls, exports: list[str]) -> list[str]:
        normalized = [name.strip() for name in exports]
        if any(not name for name in normalized):
            raise ValueError("Export names must not be blank.")
        return normalized


class AnalysisResult(BaseModel):
    compatible: bool
    risks: list[str]
    evidence: list[str]
    recommended_next_step: str