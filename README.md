# Vector_Distance_Logging

An educational architecture mockup for Vector Distance Logging (VDL).

This repository is an educational, synthetic demonstration of the architecture
behind Vector Distance Logging: observing how fabricated representations of an
AI system's input and output differ from supplied reference representations,
then recording those measurements with evidence paths.

このリポジトリは、Vector Distance Logging（VDL）の考え方を説明するための
完全合成・教育用mockupです。AIへの入力と出力を表す架空Vectorを、あらかじめ
与えられた架空Referenceと比較し、距離と時間変化をEvidence Path付きで記録します。

このmockupは本番VDLの簡略実装ではありません。実際のRepresentation生成、
Referenceの生成・更新、距離方式の選択・統合、校正、閾値、診断、運用判断を
含みません。出力を安全性、品質、適合性、異常、またはDriftの判定として
使用しないでください。

This mockup is not a simplified production VDL implementation. It does not include
production representation generation, reference construction or updates,
distance selection or combination, calibration, thresholds, diagnosis, or
operational decisions. Its output must not be interpreted as a safety, quality,
suitability, anomaly, or drift judgment.

## The idea

Real systems can convert text or other observations into comparable
representations; embeddings are one general example. This mockup does not create
embeddings or use any model. It starts with fixed, hand-authored two-dimensional
vectors that have no relationship to operational data or distributions.

```text
Concept only (not implemented here)

Text / AI interaction
        |
        v
Comparable representation (for example, an embedding)

mockup starts here

Supplied reference input  <->  observed input
                                      |
                                      v
                                     AI
                                      |
                                      v
Supplied reference output <->  observed output
                 |
                 v
Structural validation of supplied synthetic vectors
                 |
                 v
mockup Euclidean distance and change from the previous observation
                 |
                 v
Structured measurements -> evidence paths -> JSON

mockup ends here

Assessment, scoring, calibration, decisions, recommendations, and control
are not included.
```

Distance is a measurement signal, not a conclusion. This mockup never decides
whether a measurement is good, bad, safe, unsafe, stable, or drifting.

## What the code demonstrates

- a public schema with supplied synthetic input/output references;
- separate observations of fabricated input and output vectors;
- an explicitly illustrative `mockup_euclidean` distance;
- change between consecutive synthetic observations;
- structural checks required to form the measurements;
- evidence paths that identify the inputs used without copying vector values;
- deterministic machine-readable JSON; and
- strict separation between measurement and operational interpretation.

The mockup does not generate, learn, or update a reference. Reference vectors are
already present in the input. The public schema was designed independently for
education and does not map to a production schema.

## Synthetic scenarios

The `examples/` directory contains three author-labeled demonstrations:

- `stable_input.json`: input and output remain at their supplied references;
- `input_shift_input.json`: only the fabricated input moves; and
- `output_drift_input.json`: the fabricated output changes over time.

These filenames are teaching labels chosen by the authors. The program does not
classify a scenario or infer any label from the measured values.

## Requirements

- Python 3.11 or later
- no runtime dependencies outside the Python standard library

On Windows, the publication verifier requires Python 3.12 or later so junctions
can be rejected reliably. The mockup package and tests remain Python 3.11-compatible.

## Run an example

From the repository root:

```powershell
$env:PYTHONPATH = "src"
python -B -m vdl_architecture_mockup examples/stable_input.json
```

On a POSIX shell:

```sh
PYTHONPATH=src python -B -m vdl_architecture_mockup examples/stable_input.json
```

Use `--output result.json` to write JSON to a file. Each checked-in input has a
matching expected-output fixture.

## Verify before publication

```powershell
python -B -m unittest discover -s tests -v
python -B scripts/verify_public_release.py
```

The verifier enforces an explicit file allowlist and scans text files for common
secret shapes, personal paths, email addresses, and disallowed artifacts. It is
only one release gate; complete the human checks in
[`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md) as well.

## Documentation

- [`docs/VDL_CONCEPT.md`](docs/VDL_CONCEPT.md) explains the measurement idea.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) explains the software flow.
- [`docs/PUBLIC_BOUNDARY.md`](docs/PUBLIC_BOUNDARY.md) defines what is omitted.
- [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md) records publication gates.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) defines the clean-room contribution rule.
- [`SECURITY.md`](SECURITY.md) explains how to report a suspected leak.

## License

MIT. Copyright (c) 2026 Yosuke Hayakawa. See [`LICENSE`](LICENSE).
