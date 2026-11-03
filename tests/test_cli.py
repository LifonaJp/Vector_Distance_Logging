from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vdl_architecture_mockup.cli import main  # noqa: E402


class CliTests(unittest.TestCase):
    def test_cli_writes_expected_output(self) -> None:
        expected = json.loads(
            (ROOT / "examples" / "stable_output.json").read_text("utf-8")
        )
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "result.json"
            exit_code = main(
                [
                    str(ROOT / "examples" / "stable_input.json"),
                    "--output",
                    str(output_path),
                ]
            )
            actual = json.loads(output_path.read_text("utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(actual, expected)

    def test_cli_reports_invalid_json_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "invalid.json"
            input_path.write_text("not json", encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main([str(input_path)])
        self.assertEqual(exit_code, 2)
        self.assertEqual(stderr.getvalue(), "input error: invalid JSON\n")
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_cli_does_not_echo_missing_input_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "private-looking-name.json"
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main([str(input_path)])
        self.assertEqual(exit_code, 2)
        self.assertEqual(stderr.getvalue(), "input error: unable to read the input file\n")
        self.assertNotIn("private-looking-name", stderr.getvalue())

    def test_cli_reports_schema_error_without_details(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "invalid-schema.json"
            input_path.write_text('{"private_field": "private value"}', encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main([str(input_path)])
        self.assertEqual(exit_code, 2)
        self.assertEqual(
            stderr.getvalue(),
            "input error: document does not match the public schema\n",
        )
        self.assertNotIn("private", stderr.getvalue())

    def test_cli_rejects_distance_overflow_without_traceback(self) -> None:
        payload = {
            "observation_series": {
                "reference": {
                    "input_vector": [1e308, 0],
                    "output_vector": [0, 0],
                },
                "observations": [
                    {
                        "step": 0,
                        "input_vector": [-1e308, 0],
                        "output_vector": [0, 0],
                    }
                ],
            }
        }
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "overflow.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main([str(input_path)])
        self.assertEqual(exit_code, 2)
        self.assertEqual(
            stderr.getvalue(),
            "input error: document does not match the public schema\n",
        )
        self.assertNotIn("Traceback", stderr.getvalue())
        self.assertNotIn("Infinity", stderr.getvalue())

    def test_cli_serialization_guard_rejects_non_finite_result(self) -> None:
        stderr = io.StringIO()
        with (
            patch("vdl_architecture_mockup.cli.evaluate", return_value={"value": float("inf")}),
            redirect_stderr(stderr),
        ):
            exit_code = main([str(ROOT / "examples" / "stable_input.json")])
        self.assertEqual(exit_code, 3)
        self.assertEqual(
            stderr.getvalue(),
            "output error: unable to serialize the result\n",
        )
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_cli_prints_json_when_output_is_omitted(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main([str(ROOT / "examples" / "stable_input.json")])
        self.assertEqual(exit_code, 0)
        self.assertTrue(
            all(item["passed"] for item in json.loads(stdout.getvalue())["checks"])
        )


if __name__ == "__main__":
    unittest.main()
