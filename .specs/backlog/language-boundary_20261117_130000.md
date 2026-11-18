# Language boundary backport (#35)

- [x] `bin/check_description_sync.sh` + `bin/lib/description_sources.py`: pt-BR language check of the manifest description (blueprintx#1179)
- [x] `.github/workflows/tests.yml`: run Description Sync under `GITHUB_TOKEN`
- [x] `bin/check_docs_language.py`: root `CONTRIBUTING.md` joins the page set (blueprintx#1182)
- [x] `CONTRIBUTING.md` in pt-BR; `.codespellrc` skips it
- [x] `SECURITY.md`: English policy with one pt-BR line pointing at the reporting channel
- [x] Tests: description language gate (should-fail), CONTRIBUTING.md in the docs-language gate
- [x] `README.md`, `mkdocs.yml`, `pyproject.toml`: description reworded so it reads as pt-BR (the new gate rejected the old one); the GitHub About text must be updated to match
