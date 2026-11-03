"""Command-line interface for the synthetic VDL architecture mockup."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .models import InputError
from .pipeline import evaluate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Measure fabricated vectors in an educational VDL architecture mockup."
    )
    parser.add_argument("input", type=Path, help="Path to a UTF-8 synthetic JSON input")
    parser.add_argument("--output", type=Path, help="Optional path for JSON measurements")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = evaluate(payload)
    except OSError:
        print("input error: unable to read the input file", file=sys.stderr)
        return 2
    except json.JSONDecodeError:
        print("input error: invalid JSON", file=sys.stderr)
        return 2
    except InputError:
        print("input error: document does not match the public schema", file=sys.stderr)
        return 2

    try:
        rendered = json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        ) + "\n"
    except ValueError:
        print("output error: unable to serialize the result", file=sys.stderr)
        return 3
    if args.output is None:
        print(rendered, end="")
    else:
        try:
            args.output.write_text(rendered, encoding="utf-8")
        except OSError:
            print("output error: unable to write the output file", file=sys.stderr)
            return 3
    return 0
