from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vdl_architecture_mockup.models import InputError, parse_series  # noqa: E402


def valid_payload() -> dict[str, object]:
    return json.loads((ROOT / "examples" / "stable_input.json").read_text("utf-8"))


class ModelTests(unittest.TestCase):
    def test_parses_supplied_reference_and_observations(self) -> None:
        series = parse_series(valid_payload())
        self.assertEqual(series.reference.input_vector, (0.0, 0.0))
        self.assertEqual([item.step for item in series.observations], [0, 1])

    def test_unknown_fields_are_rejected(self) -> None:
        payload = valid_payload()
        payload["observation_series"]["unexpected"] = True
        with self.assertRaisesRegex(InputError, "unknown fields"):
            parse_series(payload)

    def test_observations_must_be_an_array(self) -> None:
        payload = valid_payload()
        payload["observation_series"]["observations"] = {}
        with self.assertRaisesRegex(InputError, "observations must be an array"):
            parse_series(payload)

    def test_boolean_vector_component_is_rejected(self) -> None:
        payload = valid_payload()
        payload["observation_series"]["reference"]["input_vector"][0] = True
        with self.assertRaisesRegex(InputError, "finite number"):
            parse_series(payload)

    def test_non_finite_vector_components_are_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                payload = valid_payload()
                payload["observation_series"]["reference"]["input_vector"][0] = value
                with self.assertRaisesRegex(InputError, "finite number"):
                    parse_series(payload)

    def test_boolean_step_is_rejected(self) -> None:
        payload = valid_payload()
        payload["observation_series"]["observations"][0]["step"] = False
        with self.assertRaisesRegex(InputError, "must be an integer"):
            parse_series(payload)


if __name__ == "__main__":
    unittest.main()
