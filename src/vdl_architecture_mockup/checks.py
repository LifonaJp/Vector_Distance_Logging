"""Structural checks for the synthetic measurement demonstration.

These checks validate whether a measurement can be formed. They do not judge
the size or meaning of a distance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .models import ObservationSeries


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    passed: bool
    evidence_ids: tuple[str, ...]
    message: str

    def as_dict(self) -> dict[str, object]:
        return {
            "check_id": self.check_id,
            "passed": self.passed,
            "evidence_ids": list(self.evidence_ids),
            "message": self.message,
        }


Check = Callable[[ObservationSeries], CheckResult]


def check_reference_vectors(series: ObservationSeries) -> CheckResult:
    passed = bool(series.reference.input_vector) and bool(
        series.reference.output_vector
    )
    return CheckResult(
        check_id="reference_vectors_present",
        passed=passed,
        evidence_ids=(
            "observation_series.reference.input_vector",
            "observation_series.reference.output_vector",
        ),
        message=(
            "Synthetic reference vectors are present."
            if passed
            else "Synthetic reference vectors must be non-empty."
        ),
    )


def check_observations_present(series: ObservationSeries) -> CheckResult:
    passed = bool(series.observations)
    return CheckResult(
        check_id="observations_present",
        passed=passed,
        evidence_ids=("observation_series.observations",),
        message=(
            "At least one synthetic observation is present."
            if passed
            else "At least one synthetic observation is required."
        ),
    )


def check_vector_dimensions(series: ObservationSeries) -> CheckResult:
    input_size = len(series.reference.input_vector)
    output_size = len(series.reference.output_vector)
    invalid: list[str] = []
    for index, observation in enumerate(series.observations):
        if not observation.input_vector or len(observation.input_vector) != input_size:
            invalid.append(f"observation_series.observations[{index}].input_vector")
        if not observation.output_vector or len(observation.output_vector) != output_size:
            invalid.append(f"observation_series.observations[{index}].output_vector")
    passed = input_size > 0 and output_size > 0 and not invalid
    return CheckResult(
        check_id="vector_dimensions_match",
        passed=passed,
        evidence_ids=tuple(
            invalid
            or [
                "observation_series.reference.input_vector",
                "observation_series.reference.output_vector",
                "observation_series.observations",
            ]
        ),
        message=(
            "Observed vectors match their synthetic reference dimensions."
            if passed
            else "Observed vectors must match non-empty reference dimensions."
        ),
    )


def check_steps_increasing(series: ObservationSeries) -> CheckResult:
    invalid = [
        f"observation_series.observations[{index}].step"
        for index in range(1, len(series.observations))
        if series.observations[index].step <= series.observations[index - 1].step
    ]
    passed = not invalid
    return CheckResult(
        check_id="steps_strictly_increasing",
        passed=passed,
        evidence_ids=tuple(invalid or ["observation_series.observations"]),
        message=(
            "Synthetic observation steps are strictly increasing."
            if passed
            else "Synthetic observation steps must be strictly increasing."
        ),
    )


CHECKS: tuple[Check, ...] = (
    check_reference_vectors,
    check_observations_present,
    check_vector_dimensions,
    check_steps_increasing,
)
