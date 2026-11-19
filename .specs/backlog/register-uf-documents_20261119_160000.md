# Register rg, cin and per-UF inscricao_estadual in DICT_DOCUMENTS (#73)

- [x] feat/73-register-uf-documents Unit tests first: rg, cin and the 27 `inscricao_estadual_<uf>` keys, bound UF, unmask identity
- [x] feat/73-register-uf-documents `documents.py`: `rg`, `cin` (unmask_rg as normaliser) and a comprehension over the IE module's UF table with `functools.partial`
- [x] feat/73-register-uf-documents `docs/usage.md`, `docs/api/reference.md` and the module docstring updated in pt-BR
- [x] feat/73-register-uf-documents Ticked the open item in `document-registry_20261119_150000.md`
- [ ] feat/73-register-uf-documents CI green and CodeRabbit threads answered
