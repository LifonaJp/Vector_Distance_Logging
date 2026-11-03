"""Connect synthetic VDL measurements to an auditable result container."""

from __future__ import annotations

from typing import Any

from .checks import CHECKS
from .measurements import measure_series
from .models import parse_series


def evaluate(payload: Any) -> dict[str, object]:
    """Return measurements and structural checks, never an assessment."""

    series = parse_series(payload)
    checks = [check(series) for check in CHECKS]
    measurements = measure_series(series) if all(item.passed for item in checks) else ()
    return {
        "format_version": "vdl-mockup-1",
        "notice": "Synthetic measurements only; not a diagnosis.",
        "measurements": [item.as_dict() for item in measurements],
        "checks": [item.as_dict() for item in checks],
    }
