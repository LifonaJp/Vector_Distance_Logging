from __future__ import annotations

import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import verify_public_release as verifier  # noqa: E402


class ReleaseVerifierTests(unittest.TestCase):
    def test_expected_public_path_is_safe(self) -> None:
        self.assertEqual(verifier.validate_relative_path("docs/ARCHITECTURE.md"), [])

    def test_parent_traversal_is_rejected(self) -> None:
        self.assertTrue(
            any(
                "unsafe relative path" in error
                for error in verifier.validate_relative_path("../outside.txt")
            )
        )

    def test_hidden_path_is_rejected(self) -> None:
        self.assertTrue(
            any(
                "hidden path" in error
                for error in verifier.validate_relative_path("docs/.private.txt")
            )
        )

    def test_ambiguous_windows_spelling_is_rejected(self) -> None:
        errors = verifier.validate_relative_path("docs/name. ")
        self.assertTrue(any("ambiguous path spelling" in error for error in errors))

    def test_reserved_windows_name_is_rejected(self) -> None:
        self.assertTrue(
            any(
                "reserved Windows path" in error
                for error in verifier.validate_relative_path("docs/CON")
            )
        )

    def test_non_normalized_unicode_is_rejected(self) -> None:
        decomposed = "docs/cafe\u0301.md"
        self.assertTrue(
            any(
                "non-normalized Unicode path" in error
                for error in verifier.validate_relative_path(decomposed)
            )
        )

    def test_only_implied_directories_are_allowed(self) -> None:
        self.assertEqual(
            verifier.allowed_directories(),
            {
                "docs",
                "examples",
                "scripts",
                "src",
                "src/vdl_architecture_mockup",
                "tests",
            },
        )

    def test_git_metadata_file_is_rejected_before_skip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").write_text("gitdir: elsewhere", encoding="utf-8")
            with (
                patch.object(verifier, "ROOT", root),
                patch.object(verifier, "ALLOWED_FILES", set()),
            ):
                _, errors = verifier.candidate_files()
        self.assertIn(".git must be absent or an ordinary local directory", errors)

    def test_windows_python_311_is_rejected_for_release_scan(self) -> None:
        stdout = StringIO()
        with (
            patch.object(verifier.os, "name", "nt"),
            patch.object(verifier.sys, "version_info", (3, 11, 9)),
            redirect_stdout(stdout),
        ):
            exit_code = verifier.main()
        self.assertEqual(exit_code, 1)
        self.assertIn("requires Python 3.12 or later", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
