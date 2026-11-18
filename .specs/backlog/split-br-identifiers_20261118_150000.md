# Split br_identifiers into cpf and cnpj (#54)

- [x] refactor/54-split-br-identifiers Move `_strip_float_artifact` to `_internal/utils/float_artifact.py`; repoint all 13 importers (rg also takes `is_valid_cpf` from `cpf`); no module under `src/` imports `br_identifiers`
- [x] refactor/54-split-br-identifiers `cpf.py` and `cnpj.py` (same behaviour, alphanumeric CNPJ kept); `__init__` imports from them; `__all__` unchanged
- [x] refactor/54-split-br-identifiers Tests split into `test_cpf.py` + `test_cnpj.py`: 56 collected before, 56 after (mixed parametrized tests split by document)
- [x] refactor/54-split-br-identifiers `br_identifiers.py` kept as a shim: `DeprecationWarning` on import, removal in 2.0.0; test in `test_br_identifiers_shim.py` (`pytest.warns` + `importlib.reload`)
- [x] refactor/54-split-br-identifiers Contract ("non-`str` raises `TypeError`") moved to the package docstring; module docstrings point to `:mod:pure_docs_br`
- [x] refactor/54-split-br-identifiers `CHANGELOG.md` is commitizen-generated ("do not edit by hand"): release notes are auto-generated (`generate_release_notes: true`), so the PR body does not reach them. Route: after the release that ships #54 publishes, the orchestrator appends the deprecation note (`pure_docs_br.br_identifiers` is deprecated, removal in 2.0.0, import from `pure_docs_br` instead) to the GitHub release body with `gh release edit`; workflows untouched
- [ ] Remove `br_identifiers.py` and its shim test in 2.0.0
