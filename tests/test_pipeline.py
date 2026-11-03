from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vdl_architecture_mockup import InputError, evaluate  # noqa: E402


def example(name: str) -> dict[str, object]:
    return json.loads((ROOT / "examples" / name).read_text("utf-8"))


def collect_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        nested = (collect_keys(item) for item in value.values())
        return set(value) | set().union(*nested)
    if isinstance(value, list):
        return set().union(*(collect_keys(item) for item in value))
    return set()


class PipelineTests(unittest.TestCase):
    def test_all_examples_match_expected_outputs(self) -> None:
        for scenario in ("stable", "input_shift", "output_drift"):
            with self.subTest(scenario=scenario):
                payload = example(f"{scenario}_input.json")
                expected = example(f"{scenario}_output.json")
                self.assertEqual(evaluate(payload), expected)

    def test_output_is_deterministic(self) -> None:
        payload = example("output_drift_input.json")
        self.assertEqual(evaluate(payload), evaluate(payload))

    def test_json_outputs_never_contain_non_finite_tokens(self) -> None:
        for scenario in ("stable", "input_shift", "output_drift"):
            with self.subTest(scenario=scenario):
                rendered = json.dumps(
                    evaluate(example(f"{scenario}_input.json")),
                    allow_nan=False,
                )
                self.assertNotIn("NaN", rendered)
                self.assertNotIn("Infinity", rendered)

    def test_dimension_failure_suppresses_measurements(self) -> None:
        payload = example("stable_input.json")
        payload["observation_series"]["observations"][1]["input_vector"] = [0]
        result = evaluate(payload)
        checks = {item["check_id"]: item for item in result["checks"]}
        self.assertEqual(result["measurements"], [])
        self.assertFalse(checks["vector_dimensions_match"]["passed"])
        self.assertEqual(
            checks["vector_dimensions_match"]["evidence_ids"],
            ["observation_series.observations[1].input_vector"],
        )

    def test_duplicate_step_suppresses_measurements(self) -> None:
        payload = example("stable_input.json")
        payload["observation_series"]["observations"][1]["step"] = 0
        result = evaluate(payload)
        checks = {item["check_id"]: item for item in result["checks"]}
        self.assertEqual(result["measurements"], [])
        self.assertFalse(checks["steps_strictly_increasing"]["passed"])

    def test_empty_reference_suppresses_measurements(self) -> None:
        payload = example("stable_input.json")
        payload["observation_series"]["reference"]["input_vector"] = []
        result = evaluate(payload)
        self.assertEqual(result["measurements"], [])
        self.assertTrue(any(not item["passed"] for item in result["checks"]))

    def test_missing_reference_is_rejected_instead_of_generated(self) -> None:
        payload = example("stable_input.json")
        del payload["observation_series"]["reference"]
        with self.assertRaisesRegex(InputError, "reference is required"):
            evaluate(payload)

    def test_input_is_not_mutated_or_updated(self) -> None:
        payload = example("input_shift_input.json")
        original = copy.deepcopy(payload)
        evaluate(payload)
        self.assertEqual(payload, original)

    def test_result_has_no_interpretation_capabilities(self) -> None:
        result = evaluate(example("output_drift_input.json"))
        forbidden = {
            "meaning",
            "assessment",
            "trend_class",
            "risk",
            "score",
            "severity",
            "drift_state",
            "decision",
            "recommendation",
            "threshold",
            "weight",
            "alert",
            "drift_probability",
        }
        self.assertTrue(forbidden.isdisjoint(collect_keys(result)))

    def test_author_scenario_labels_are_not_inferred(self) -> None:
        rendered = json.dumps(evaluate(example("output_drift_input.json")))
        self.assertNotIn("output_drift", rendered)
        self.assertNotIn("input_shift", rendered)
        self.assertNotIn("stable", rendered)


if __name__ == "__main__":
    unittest.main()
