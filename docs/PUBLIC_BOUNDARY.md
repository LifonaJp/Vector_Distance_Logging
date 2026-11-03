# Public boundary

## Included

- the VDL measurement concept;
- AI input and output as separate observation subjects;
- comparable representations, with embeddings mentioned as a general example;
- supplied synthetic input/output references;
- supplied synthetic two-dimensional observations;
- an illustrative Euclidean distance;
- change from the previous supplied observation;
- structural validation, evidence paths, and deterministic JSON; and
- three independently authored synthetic teaching scenarios.

## Not included

- representation or embedding generation;
- any model, model configuration, dimensions, pooling, or normalization;
- production reference construction, selection, learning, or updates;
- production distance metrics, combinations, feature choices, or rationales;
- historical windows or production time-series handling;
- calibrated probabilities, thresholds, weights, categories, or severity;
- alerts, hard-fail rules, aggregate decisions, or recommendations;
- prompts, operational policies, customer context, or production data;
- an assessment engine, control layer, or report renderer; or
- any mapping from the mockup to a production implementation or schema.

The words *drift*, *assessment*, and *recommendation* may appear in documentation
to explain what the mockup does not do. They are not output capabilities.

## Provenance rule

All public source, schemas, examples, and explanations must begin from this public
boundary and be independently authored. Do not copy, simplify, rename, translate,
or patch private source, data, identifiers, categories, formulas, or documentation.

Every change requires renewed functional, leakage, provenance, and similarity
review. A previous approval does not carry over to an updated candidate.
