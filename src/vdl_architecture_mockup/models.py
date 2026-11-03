"""Strict public models for fully synthetic VDL observations."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


class InputError(ValueError):
    """Raised when input does not match the public educational schema."""


Vector = tuple[float, ...]


@dataclass(frozen=True)
class Reference:
    input_vector: Vector
    output_vector: Vector


@dataclass(frozen=True)
class Observation:
    step: int
    input_vector: Vector
    output_vector: Vector


@dataclass(frozen=True)
class ObservationSeries:
    reference: Reference
    observations: tuple[Observation, ...]


def _expect_object(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise InputError(f"{path} must be an object")
    return value


def _expect_array(value: Any, path: str) -> Sequence[Any]:
    if not isinstance(value, list):
        raise InputError(f"{path} must be an array")
    return value


def _reject_unknown_keys(
    value: Mapping[str, Any], allowed: set[str], path: str
) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise InputError(f"{path} contains unknown fields")


def _expect_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{path} must be a finite number")
    rendered = float(value)
    if not math.isfinite(rendered):
        raise InputError(f"{path} must be a finite number")
    return rendered


def _expect_step(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InputError(f"{path} must be an integer")
    return value


def _parse_vector(value: Any, path: str) -> Vector:
    return tuple(
        _expect_number(item, f"{path}[{index}]")
        for index, item in enumerate(_expect_array(value, path))
    )


def _require_fields(value: Mapping[str, Any], required: tuple[str, ...], path: str) -> None:
    for field in required:
        if field not in value:
            raise InputError(f"{path}.{field} is required")


def parse_series(payload: Any) -> ObservationSeries:
    """Parse JSON-compatible data without applying operational judgments."""

    root = _expect_object(payload, "root")
    _reject_unknown_keys(root, {"observation_series"}, "root")
    if "observation_series" not in root:
        raise InputError("root.observation_series is required")

    series = _expect_object(root["observation_series"], "observation_series")
    _reject_unknown_keys(series, {"reference", "observations"}, "observation_series")
    _require_fields(series, ("reference", "observations"), "observation_series")

    raw_reference = _expect_object(
        series["reference"], "observation_series.reference"
    )
    _reject_unknown_keys(
        raw_reference,
        {"input_vector", "output_vector"},
        "observation_series.reference",
    )
    _require_fields(
        raw_reference,
        ("input_vector", "output_vector"),
        "observation_series.reference",
    )
    reference = Reference(
        input_vector=_parse_vector(
            raw_reference["input_vector"],
            "observation_series.reference.input_vector",
        ),
        output_vector=_parse_vector(
            raw_reference["output_vector"],
            "observation_series.reference.output_vector",
        ),
    )

    observations: list[Observation] = []
    for index, item in enumerate(
        _expect_array(series["observations"], "observation_series.observations")
    ):
        path = f"observation_series.observations[{index}]"
        raw_observation = _expect_object(item, path)
        _reject_unknown_keys(
            raw_observation, {"step", "input_vector", "output_vector"}, path
        )
        _require_fields(
            raw_observation, ("step", "input_vector", "output_vector"), path
        )
        observations.append(
            Observation(
                step=_expect_step(raw_observation["step"], f"{path}.step"),
                input_vector=_parse_vector(
                    raw_observation["input_vector"], f"{path}.input_vector"
                ),
                output_vector=_parse_vector(
                    raw_observation["output_vector"], f"{path}.output_vector"
                ),
            )
        )

    return ObservationSeries(reference=reference, observations=tuple(observations))
