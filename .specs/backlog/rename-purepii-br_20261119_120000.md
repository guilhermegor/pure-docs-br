# Rename pure-docs-br to purepii-br (#63)

- [x] chore/rename-purepii-br `git mv src/pure_docs_br src/purepii_br`; every `pure-docs-br` / `pure_docs_br` in tracked files replaced, `.specs/backlog/` left as historical record
- [x] chore/rename-purepii-br `version("purepii-br")` in `__init__.py` follows the distribution name; suite green
- [x] chore/rename-purepii-br README overview says the package validates and formats identifiers, not LGPD redaction
- [x] chore/rename-purepii-br Deprecated `br_identifiers` shim removed (promised for 2.0.0)
- [x] GitHub repo renamed to `guilhermegor/purepii-br` (before the first publish: the OIDC publisher names it); homepage updated; merged as #70
- [x] chore/63-rename-backfill `backfill=true` input on both release workflows (rebuild every `vX.Y.Z` under `purepii-br`, `skip-existing`); local dry run on v1.0.0 and v1.17.0 installs and reports the tag version
- [x] docs/rename-ledger-done 2.0.0 published to Test PyPI then PyPI; history backfilled (20 versions on both indexes); `pip install purepii-br` + `import purepii_br` verified
- [x] docs/rename-ledger-done Local dir `~/github/pure-docs-br` -> `~/github/purepii-br` (VS Code closed; `git worktree repair` before any prune) and the project memory dir renamed to match
- [x] docs/rename-ledger-done Downstream: blueprintx#1212 (closed via blueprintx#1218), profile README (guilhermegor/guilhermegor#11), greenfield spec (greenfield#105; #94 stays closed), `ROADMAP_BOARDS` (no longer exists, boards are discovered by title), kanban title
- [x] docs/rename-ledger-done Old `pure-docs-br` deleted on Test PyPI then PyPI, only after consumers moved (JSON API and simple index return 404)
