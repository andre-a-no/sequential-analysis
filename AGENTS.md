# Working on sequential-analysis

Read [CONTRIBUTING.md](CONTRIBUTING.md), [README.md](README.md) and
[the plain-language overview](docs/overview.md). This is the mathematical
statistical layer; application workflows and live action execution belong in
`sequentialist-*`. Keep statistical procedures separate from acquisition,
delivery, topology, persistence and consumers.

## Development and verification

- Import: `sequential_analysis`; Python 3.8+ compatibility is part of the API.
- Install the checkout: `python -m pip install -e '.[fast,plot,test]'`.
- Python tests: `python -W error::ResourceWarning -m unittest discover -s tests -t .`.
- TypeScript: from `ts/`, run `npm ci` then `npm test`. After building, from the
  root run `REQUIRE_TYPESCRIPT=1 python -m unittest tests.test_typescript -v`.
- Before code publication use the checks in `.github/workflows/tests.yml`:
  `ruff check .`, `mypy` and
  `vermin --no-tips --violations -t=3.8- src tests tools examples`
  with the CI-pinned version of vermin. Run
  relevant regression tests for changes to inference, persistence or delivery.
- For prose-only edits, verify changed links and navigation and run the relevant
  named tests in `tests.test_docs`. Avoid rerunning every documentation Python
  simulation when neither code blocks nor inference behavior changed.

## Documentation pipeline

`mkdocs.yml` owns navigation. `tools/mkdocs_hooks.py` generates the published
`llms-full.txt`; `docs/llms.txt` is the published curated index. Root `llms.txt`
is a repository entry point, not a replacement for those files. Add a new
non-guide page to navigation. Changes under `docs/guide/` must preserve the
translation contract checked by `test_translations_match_the_original`.
Use `mkdocs build --strict` when the pinned documentation dependencies are
installed; use the versions in `.github/workflows/docs.yml`.

Do not raise the Python minimum, add mandatory dependencies, rewrite lockfiles,
or change statistical claims incidentally. Preserve `from __future__ import
annotations` and compatibility helpers described in CONTRIBUTING. New source
files use the existing SPDX header. Follow the CLA/licensing policy before
contributing code; do not merge or publish without the requested scope.

Every statistical conclusion retains its exact/asymptotic/model/approximate/none
meaning and assumptions. Compare methods with independent references where
available. A development checkout, released package and deployed documentation
are separate versions; do not claim they are identical without checking.

Keep discovery text factual. Do not invent citations, adoption, rankings or
assistant behavior. Instructions and llms indexes can be supplied to assistants;
their presence does not guarantee that an external service reads them.
