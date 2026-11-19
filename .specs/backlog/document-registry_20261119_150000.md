# Uniform per-document strategy with a runtime registry (#40)

- [x] feat/40-document-registry Unit tests first: registry keys, delegation to the public functions, mask-less documents, unknown key, frozen strategy
- [x] feat/40-document-registry `DocumentStrategy` immutable NamedTuple and `DICT_DOCUMENTS` registry in `documents.py`, exported via `__all__`
- [x] feat/40-document-registry `docs/usage.md` section and `docs/api/reference.md` entry in pt-BR
- [ ] Open: `inscricao_estadual` and `rg`/`cin` are not registered, their functions need a `str_uf` argument the uniform `(str_value)` interface cannot carry
