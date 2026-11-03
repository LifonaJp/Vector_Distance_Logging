# Architecture

## Purpose

The mockup connects two ideas without supplying operational evaluation ability:

1. an illustrative VDL measurement layer over fabricated vectors; and
2. an outer evaluation pipeline that validates, traces, and serializes results.

The first layer measures. The second makes measurements auditable. Neither layer
interprets their operational meaning.

## Responsibility flow

```text
AI input/output
  -> representation                       concept only
  -> supplied synthetic vectors            mockup boundary begins
  -> supplied synthetic references
  -> structural validation
  -> mockup_euclidean distance
  -> change from previous observation
  -> structured measurements
  -> evidence trace
  -> JSON result                           mockup boundary ends
  -> assessment / interpretation           not included
  -> report / presentation                 not included in v2
```

The documentation may mention embeddings as a general example of a comparable
representation. The package contains no embedding model, model name, vectorizer,
network call, representation-generation code, or production representation data.

## Public input model

The root contains one `observation_series` with:

- `reference.input_vector` and `reference.output_vector`: supplied, fabricated
  reference vectors;
- `observations[].step`: an author-provided integer ordering value; and
- `observations[].input_vector` and `observations[].output_vector`: supplied,
  fabricated observed vectors.

The mockup does not generate, learn, select, or update a reference. The schema was
designed for this educational repository and has no production-field mapping.

## Measurement model

For each observation the mockup emits four independent measurement entries:

- `input_reference_distance`;
- `output_reference_distance`;
- `input_change_from_previous`; and
- `output_change_from_previous`.

Every entry has only:

- `measurement_id`;
- `measurement_method`;
- `step`;
- `value`; and
- `evidence_ids`.

The first change measurement is `null` because no previous observation exists.
This is different from a measured change of zero.

`mockup_euclidean` is textbook Euclidean distance over synthetic vectors. It is
illustrative only and does not represent a production VDL method. The mockup does
not compare alternative metrics or explain metric selection or normalization.

## Structural checks

Checks only determine whether the supplied synthetic data can be measured:

- reference vectors are non-empty;
- at least one observation exists;
- observed dimensions match their corresponding references; and
- steps are strictly increasing.

Finite-number and integer parsing also reject NaN, infinity, and Boolean values.
No check considers whether a distance is large, unusual, acceptable, or drifting.

## Evidence behavior

A reference-distance measurement points to the relevant supplied reference and
current observation paths. A change measurement points to the current and
previous observation paths. The result never copies vector components.

## Modules

- `models.py` parses strict, immutable synthetic data objects.
- `measurements.py` implements the explicitly illustrative measurement method.
- `checks.py` contains measurement-formation checks only.
- `pipeline.py` coordinates parsing, checking, measurement, and serialization.
- `cli.py` provides fixed-error file and standard-output handling.

There is no network access, model call, database, plugin, telemetry, external
service, runtime configuration, assessment engine, or report renderer. Runtime
dependencies are empty.
