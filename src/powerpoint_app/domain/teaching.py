"""Teaching contracts shared by the CLI, desktop editor and planner."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TeachingModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class TeachingProfile(TeachingModel):
    profile_version: Literal["1.0"] = "1.0"
    subject: str = "Teknisk matematik og fysik"
    audience: str = "Maskinmesterstuderende på 4. semester"
    prior_knowledge: list[str] = Field(default_factory=list)
    learning_objectives: list[str] = Field(min_length=1)
    practical_context: str = ""
    required_method: str = ""
    notation: list[str] = Field(default_factory=list)
    support: Literal["beginner", "guided", "revision"] = "guided"
    duration_minutes: int = Field(default=15, ge=1, le=600)
    approximate_slides: int = Field(default=10, ge=1, le=100)


class Question(TeachingModel):
    prompt: str = Field(min_length=1, max_length=350)
    answer: str = Field(min_length=1, max_length=350)
    explanation: str = Field(min_length=1, max_length=450)
    wait_seconds: int = Field(default=30, ge=5, le=600)


class TeachingSlide(TeachingModel):
    stage: Literal["context", "explanation", "worked_example", "guided_practice", "independent_practice", "retrieval", "transfer", "summary"]
    objective_indices: list[int] = Field(min_length=1)
    question: Question | None = None
    assumptions: list[str] = Field(default_factory=list)


class Quantity(TeachingModel):
    value: float
    unit: str = Field(min_length=1, max_length=30)


class CalculationCheck(TeachingModel):
    element_id: str = Field(min_length=1)
    expression: str = Field(min_length=1, max_length=200)
    quantities: dict[str, Quantity] = Field(min_length=1, max_length=20)
    expected: Quantity
    relative_tolerance: float = Field(default=0.001, ge=0, le=0.01)

    @model_validator(mode="after")
    def valid_variable_names(self):
        if any(not name.isidentifier() or name.startswith("_") for name in self.quantities):
            raise ValueError("Beregningsvariable skal være navne uden indledende underscore.")
        return self
