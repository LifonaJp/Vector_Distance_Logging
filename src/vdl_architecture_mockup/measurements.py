"""Textbook measurements over fabricated vectors.

The ``mockup_euclidean`` method is illustrative only. It is not a production VDL
method and does not select, normalize, combine, or interpret distance signals.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .models import InputError, ObservationSeries, Vector


def mockup_euclidean(left: Vector, right: Vector) -> float:
    """Return a rounded textbook distance for deterministic mockup output."""

    distance = math.dist(left, right)
    if not math.isfinite(distance):
        raise InputError("mockup measurement must be finite")
    return round(distance, 6)


@dataclass(frozen=True)
class Measurement:
    measurement_id: str
    measurement_method: str
    step: int
    value: float | None
    evidence_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "measurement_id": self.measurement_id,
            "measurement_method": self.measurement_method,
            "step": self.step,
            "value": self.value,
            "evidence_ids": list(self.evidence_ids),
        }


def _reference_measurement(
    *, measurement_id: str, step: int, observed: Vector, reference: Vector,
    observed_path: str, reference_path: str
) -> Measurement:
    return Measurement(
        measurement_id=measurement_id,
        measurement_method="mockup_euclidean",
        step=step,
        value=mockup_euclidean(observed, reference),
        evidence_ids=(reference_path, observed_path),
    )


def _change_measurement(
    *, measurement_id: str, step: int, current: Vector,
    previous: Vector | None, current_path: str, previous_path: str | None
) -> Measurement:
    return Measurement(
        measurement_id=measurement_id,
        measurement_method="mockup_euclidean",
        step=step,
        value=None if previous is None else mockup_euclidean(current, previous),
        evidence_ids=(
            (current_path,)
            if previous_path is None
            else (previous_path, current_path)
        ),
    )


def measure_series(series: ObservationSeries) -> tuple[Measurement, ...]:
    """Measure distance and change without classifying their meaning."""

    measured: list[Measurement] = []
    previous_input: Vector | None = None
    previous_output: Vector | None = None

    for index, observation in enumerate(series.observations):
        base = f"observation_series.observations[{index}]"
        previous_base = (
            None if index == 0 else f"observation_series.observations[{index - 1}]"
        )
        measured.extend(
            [
                _reference_measurement(
                    measurement_id="input_reference_distance",
                    step=observation.step,
                    observed=observation.input_vector,
                    reference=series.reference.input_vector,
                    observed_path=f"{base}.input_vector",
                    reference_path="observation_series.reference.input_vector",
                ),
                _reference_measurement(
                    measurement_id="output_reference_distance",
                    step=observation.step,
                    observed=observation.output_vector,
                    reference=series.reference.output_vector,
                    observed_path=f"{base}.output_vector",
                    reference_path="observation_series.reference.output_vector",
                ),
                _change_measurement(
                    measurement_id="input_change_from_previous",
                    step=observation.step,
                    current=observation.input_vector,
                    previous=previous_input,
                    current_path=f"{base}.input_vector",
                    previous_path=(
                        None if previous_base is None else f"{previous_base}.input_vector"
                    ),
                ),
                _change_measurement(
                    measurement_id="output_change_from_previous",
                    step=observation.step,
                    current=observation.output_vector,
                    previous=previous_output,
                    current_path=f"{base}.output_vector",
                    previous_path=(
                        None
                        if previous_base is None
                        else f"{previous_base}.output_vector"
                    ),
                ),
            ]
        )
        previous_input = observation.input_vector
        previous_output = observation.output_vector
    return tuple(measured)
