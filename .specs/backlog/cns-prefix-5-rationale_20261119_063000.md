# Document why a 5-prefixed CNS is rejected (#55)

- [x] docs/55-cns-prefix-5-rationale `docs/usage.md` CNS section: new subsection with the accepted prefixes, the rejection of `5`, the sources on each side (DATASUS Wayback copy, ANVISA, e-SUS APS), the reason, the cost and what would reopen it
- [x] docs/55-cns-prefix-5-rationale `is_valid_cns` docstring and the `cns.py` module docstring point to that subsection; the module docstring no longer says "pending the owner's decision"
- [x] docs/55-cns-prefix-5-rationale `docs/api/reference.md` links the subsection
- [x] docs/55-cns-prefix-5-rationale Test pinning the decision: `500000000000002` (sum 77, divisible by 11) is `False`. The existing parametrized `5` case (`500000000010002`, sum 82) and the issue's `500000000000003` (sum 76) fail the sum anyway, so they did not pin the decision
- [x] docs/55-cns-prefix-5-rationale No behaviour change in `src/`

Completed — kept as a record.
