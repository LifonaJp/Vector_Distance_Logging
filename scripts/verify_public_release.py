"""Fail closed when the public candidate contains an unexpected artifact."""

from __future__ import annotations

import os
import re
import stat
import sys
import unicodedata
from pathlib import Path
from pathlib import PurePosixPath, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_FILES = {
    ".gitignore",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "SECURITY.md",
    "docs/ARCHITECTURE.md",
    "docs/PUBLIC_BOUNDARY.md",
    "docs/RELEASE_CHECKLIST.md",
    "docs/VDL_CONCEPT.md",
    "examples/input_shift_input.json",
    "examples/input_shift_output.json",
    "examples/output_drift_input.json",
    "examples/output_drift_output.json",
    "examples/stable_input.json",
    "examples/stable_output.json",
    "pyproject.toml",
    "scripts/verify_public_release.py",
    "src/vdl_architecture_mockup/__init__.py",
    "src/vdl_architecture_mockup/__main__.py",
    "src/vdl_architecture_mockup/checks.py",
    "src/vdl_architecture_mockup/cli.py",
    "src/vdl_architecture_mockup/measurements.py",
    "src/vdl_architecture_mockup/models.py",
    "src/vdl_architecture_mockup/pipeline.py",
    "tests/__init__.py",
    "tests/test_cli.py",
    "tests/test_measurements.py",
    "tests/test_models.py",
    "tests/test_pipeline.py",
    "tests/test_release_verifier.py",
}

DENIED_NAMES = {
    ".env",
    ".npmrc",
    ".pypirc",
    ".netrc",
    "desktop.ini",
    "thumbs.db",
}

DENIED_SUFFIXES = {
    ".7z",
    ".db",
    ".doc",
    ".docx",
    ".gz",
    ".ipynb",
    ".log",
    ".npy",
    ".npz",
    ".pdf",
    ".pickle",
    ".pkl",
    ".pyc",
    ".sqlite",
    ".tar",
    ".whl",
    ".xls",
    ".xlsx",
    ".zip",
}

TEXT_PATTERNS = {
    "email address": re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
    "Windows user path": re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s]+"),
    "POSIX home path": re.compile("/" + r"(?:Users|home)/[^/\s]+/"),
    "private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "common cloud access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token shape": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "OpenAI token shape": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "credential assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|client[_-]?secret|password|access[_-]?token)\s*[:=]\s*['\"][^'\"]+['\"]"
    ),
}


def allowed_directories() -> set[str]:
    directories: set[str] = set()
    for relative in ALLOWED_FILES:
        parent = PurePosixPath(relative).parent
        while parent.as_posix() != ".":
            directories.add(parent.as_posix())
            parent = parent.parent
    return directories


def validate_relative_path(relative: str) -> list[str]:
    errors: list[str] = []
    posix = PurePosixPath(relative)
    if posix.is_absolute() or any(part in {"", ".", ".."} for part in posix.parts):
        errors.append(f"unsafe relative path: {relative}")
    if unicodedata.normalize("NFC", relative) != relative:
        errors.append(f"non-normalized Unicode path: {relative}")
    if any(part.endswith((" ", ".")) or ":" in part for part in posix.parts):
        errors.append(f"ambiguous path spelling: {relative}")
    if any(PureWindowsPath(part).is_reserved() for part in posix.parts):
        errors.append(f"reserved Windows path: {relative}")
    if any(part.startswith(".") for part in posix.parts) and relative != ".gitignore":
        errors.append(f"hidden path is not allowed: {relative}")
    return errors


def is_reparse_point(path: Path) -> bool:
    """Return whether a Windows entry carries the reparse-point attribute."""

    try:
        attributes = getattr(os.lstat(path), "st_file_attributes", 0)
    except OSError:
        return False
    marker = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & marker)


def is_junction(path: Path) -> bool:
    checker = getattr(path, "is_junction", None)
    return bool(checker and checker())


def candidate_files() -> tuple[set[str], list[str]]:
    files: set[str] = set()
    errors: list[str] = []
    permitted_directories = allowed_directories()
    root_resolved = ROOT.resolve()
    pending_directories = [ROOT]

    while pending_directories:
        directory = pending_directories.pop()
        try:
            entries = list(os.scandir(directory))
        except OSError:
            relative_directory = directory.relative_to(ROOT).as_posix()
            errors.append(f"unable to inspect directory: {relative_directory}")
            continue

        for entry in entries:
            path = Path(entry.path)
            relative = path.relative_to(ROOT)
            relative_text = relative.as_posix()
            symbolic_link = entry.is_symlink()
            junction = is_junction(path)
            reparse_point = is_reparse_point(path)

            # The root Git metadata entry is inspected before its contents are
            # skipped. Only an ordinary local directory is acceptable.
            if relative_text == ".git":
                if symbolic_link or junction or reparse_point:
                    errors.append(".git must not be a link, junction, or reparse point")
                elif not entry.is_dir(follow_symlinks=False):
                    errors.append(".git must be absent or an ordinary local directory")
                continue

            errors.extend(validate_relative_path(relative_text))
            if symbolic_link or junction or reparse_point:
                files.add(relative_text)
                errors.append(f"link or reparse point is not allowed: {relative_text}")
                continue

            if entry.is_file(follow_symlinks=False):
                files.add(relative_text)
                try:
                    path.resolve(strict=True).relative_to(root_resolved)
                except (OSError, ValueError):
                    errors.append(f"file resolves outside candidate root: {relative_text}")
            elif entry.is_dir(follow_symlinks=False):
                if relative_text not in permitted_directories:
                    errors.append(f"unexpected directory: {relative_text}")
                else:
                    pending_directories.append(path)
            else:
                errors.append(f"unsupported filesystem entry: {relative_text}")
    return files, errors


def main() -> int:
    if os.name == "nt" and sys.version_info < (3, 12):
        print("public release verification failed:")
        print("- Windows release verification requires Python 3.12 or later")
        return 1

    files, errors = candidate_files()

    unexpected = sorted(files - ALLOWED_FILES)
    missing = sorted(ALLOWED_FILES - files)
    errors.extend(f"unexpected file: {path}" for path in unexpected)
    errors.extend(f"missing allowlisted file: {path}" for path in missing)

    for relative in sorted(files):
        path = ROOT / relative
        if path.name.lower() in DENIED_NAMES or path.suffix.lower() in DENIED_SUFFIXES:
            errors.append(f"disallowed artifact: {relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"non-UTF-8 or binary file: {relative}")
            continue
        for label, pattern in TEXT_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label} detected in: {relative}")

    if errors:
        print("public release verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"public release verification passed ({len(files)} allowlisted files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
