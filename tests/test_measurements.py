from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vdl_architecture_mockup.measurements import (  # noqa: E402
    measure_series,
    mockup_euclidean,
)
from vdl_architecture_mockup.models import InputError, parse_series  # noqa: E402


def load_series(name: str = "input_shift_input.json"):
    payload = json.loads((ROOT / "examples" / name).read_text("utf-8"))
    return parse_series(payload)


class MeasurementTests(unittest.TestCase):
    def test_mockup_euclidean_is_textbook_distance(self) -> None:
        self.assertEqual(mockup_euclidean((0.0, 0.0), (3.0, 4.0)), 5.0)

    def test_finite_components_cannot_overflow_measurement(self) -> None:
        with self.assertRaisesRegex(InputError, "measurement must be finite"):
            mockup_euclidean((1e308, 0.0), (-1e308, 0.0))

    def test_first_previous_change_is_null_not_zero(self) -> None:
        measurements = measure_series(load_series())
        first_changes = [
            item for item in measurements[:4] if "change" in item.measurement_id
        ]
        self.assertEqual([item.value for item in first_changes], [None, None])

    def test_reference_and_change_evidence_are_exact(self) -> None:
        measurements = measure_series(load_series())
        self.assertEqual(
            measurements[4].evidence_ids,
            (
                "observation_series.reference.input_vector",
                "observation_series.observations[1].input_vector",
            ),
        )
        self.assertEqual(
            measurements[6].evidence_ids,
            (
                "observation_series.observations[0].input_vector",
                "observation_series.observations[1].input_vector",
            ),
        )

    def test_measurement_schema_is_minimal(self) -> None:
        allowed = {
            "measurement_id",
            "measurement_method",
            "step",
            "value",
            "evidence_ids",
        }
        for measurement in measure_series(load_series()):
            self.assertEqual(set(measurement.as_dict()), allowed)
            self.assertEqual(measurement.measurement_method, "mockup_euclidean")

    def test_vector_components_are_not_copied_into_result(self) -> None:
        payload = {
            "observation_series": {
                "reference": {
                    "input_vector": [12345.678, 23456.789],
                    "output_vector": [34567.891, 45678.912],
                },
                "observations": [
                    {
                        "step": 0,
                        "input_vector": [56789.123, 67891.234],
                        "output_vector": [78912.345, 89123.456],
                    }
                ],
            }
        }
        rendered = json.dumps(
            [item.as_dict() for item in measure_series(parse_series(payload))]
        )
        for component in ("12345.678", "23456.789", "34567.891", "45678.912"):
            self.assertNotIn(component, rendered)

    def test_output_shape_does_not_branch_on_distance_size(self) -> None:
        stable = [
            set(item.as_dict())
            for item in measure_series(load_series("stable_input.json"))
        ]
        shifted = [
            set(item.as_dict())
            for item in measure_series(load_series("output_drift_input.json"))
        ]
        self.assertEqual(stable, shifted[: len(stable)])


if __name__ == "__main__":
    unittest.main()
