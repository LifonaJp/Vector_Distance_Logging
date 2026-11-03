# Local-first release checklist

Do not create a remote repository, push a commit, enable automation, publish a
package, or upload an archive until every applicable local gate below is complete
and the final reviewer has approved the exact candidate tree.

## Candidate contents

- [ ] `python -B scripts/verify_public_release.py` passes from the repository root.
- [ ] On Windows, the release verifier is run with Python 3.12 or later.
- [ ] The verifier's allowlist exactly matches the intended public files.
- [ ] No untracked, hidden, generated, cached, binary, or editor artifact exists.
- [ ] Every example vector and label is independently invented for this repository.
- [ ] Source, comments, messages, help, JSON keys, and documents contain no private
      vocabulary, personal paths, or public-to-private correspondence.

## Concept integrity

- [ ] README explains input/output observation, representation, reference,
      distance, temporal change, and measurement-versus-interpretation.
- [ ] Embeddings appear only as a general documentation concept.
- [ ] No representation or embedding generation exists in code.
- [ ] Reference vectors are supplied inputs; the mockup does not create or update them.
- [ ] `mockup_euclidean` is identified as illustrative and non-production.
- [ ] Scenario filenames are author labels and are never inferred by the program.

## Behavior

- [ ] `python -B -m unittest discover -s tests -v` passes.
- [ ] All three synthetic examples match their expected JSON.
- [ ] The first previous-change measurement is `null`.
- [ ] Distance evidence points to reference and current observation paths.
- [ ] Change evidence points to previous and current observation paths.
- [ ] Vector values are not copied into output.
- [ ] No distance-based branch, classification, trend inference, or diagnosis exists.
- [ ] Serialized models and outputs have no scoring, threshold, severity,
      recommendation, decision, alert, or calibrated-probability capability.
- [ ] CLI errors remain fixed and do not echo user paths or values.

## Provenance and similarity

- [ ] Every public file was written from approved public concepts only.
- [ ] A reviewer checked terminology, schema, identifiers, structure, and text for
      unintended one-to-one correspondence with private material.
- [ ] Normalized-line, long-identifier, and token-window comparisons pass.
- [ ] No private patch, snippet, export, archive, or inherited Git history was used.

## Dependencies and license

- [ ] Runtime dependencies remain empty.
- [ ] Build-tool licenses and necessity are reviewed before any build or CI use.
- [ ] The repository owner confirms the copyright-holder wording in `LICENSE`.
- [ ] No distribution, container, release asset, or generated SBOM is included.

## Version control and hosting

- [ ] Initialize a new repository here; never inherit private objects or refs.
- [ ] Review all commit and tag metadata before publication.
- [ ] Use a deliberate public identity.
- [ ] Review hosting permissions, secrets, hooks, applications, workflows, runners,
      OIDC, fork settings, and pull-request settings before making it public.

## Final gate

- [ ] Generate a fresh evidence bundle containing every allowlisted file.
- [ ] A human reviewer approves the exact v2 candidate and records residual risks.
- [ ] Only after approval: create the remote, push, configure hosting, and publish.

Apply the complete checklist to every update; earlier approvals do not carry over.
