# Contributing

Contributions must remain independent, synthetic, and educational.

## Clean-room rule

Write changes from this public mockup's documented behavior only. Do not copy,
adapt, translate, summarize, or paste private source code, private schemas,
private prompts, internal documents, production examples, customer material,
or patches derived from them. Do not attach private workspaces to assistants,
indexers, or development tools used for this repository.

Every fixture must be invented from scratch. A renamed, shifted, hashed,
truncated, or otherwise transformed operational record is not synthetic.

## Before proposing a change

1. Add or update tests for public behavior.
2. Run `python -B -m unittest discover -s tests -v`.
3. Run `python -B scripts/verify_public_release.py`.
4. Review the diff for private identifiers, paths, comments, logs, and metadata.
5. Confirm the change does not imply a score, recommendation, or real-world
   assessment.

Changes that require private context must not be contributed to this mockup.
