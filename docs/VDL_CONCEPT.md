# Vector Distance Logging concept

## What VDL observes

Vector Distance Logging is presented here as a measurement idea: represent an
AI system's input and output in comparable spaces, compare observations with
expected references, and record distance and change as traceable signals.

It asks questions such as:

- How far is an observed input representation from its supplied reference?
- How far is an observed output representation from its supplied reference?
- How much did each representation change between observations?

It does not, by itself, answer whether those measurements are safe, unsafe,
correct, incorrect, acceptable, or abnormal.

## Representation

Text and other observations can be converted into comparable representations;
embeddings are one general example. This repository does not implement that
conversion. It begins with fixed two-dimensional vectors written specifically
for the examples.

No model, model name, dimensionality choice, pooling, normalization, shared-space
assumption, or production representation method is described or implemented.

## Reference

A reference represents an expected point for comparison. In this mockup it is an
ordinary input value supplied with each synthetic example. The mockup does not
decide what a good reference is and does not create, learn, select, or update it.

That omission is deliberate: reference construction is an operational concern,
whereas this repository demonstrates only how a supplied reference relates to a
supplied observation.

## Measurement versus interpretation

```text
measurement:     observed vector + reference vector -> distance
measurement:     previous vector + current vector   -> change
interpretation:  what those values mean             -> not included
```

Distance and change are signals. Turning signals into categories, probabilities,
alerts, scores, or decisions requires assumptions that are intentionally outside
the mockup.

## Time

Multiple observations make change visible. The first observation has no previous
state, so its change value is `null`. Later observations compare only with the
immediately preceding supplied observation. The mockup does not infer missing time,
select windows, aggregate histories, or classify a trend.

## Evidence trace

Each measurement records the JSON-like paths used to produce it. Paths support
review and reprocessing without repeating vector values in the result.
