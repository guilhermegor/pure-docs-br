# Certidão matrícula support (#32)

- [x] feat/32-certidao-matricula `is_valid_certidao_matricula`, `mask_certidao_matricula`, `unmask_certidao_matricula` in `src/pure_docs_br/certidao_matricula.py`, exported from the package root; one family for birth, marriage and death certificates
- [x] feat/32-certidao-matricula DV formula: mod 11 over 30 then 31 digits, remainder 10 = 1 (weights from the issue). Source: ghiorzi.org/DVnew.htm (secondary; not in the CNJ provimentos); reproduces the source example (sums 288 and 309, DV 21)
- [x] feat/32-certidao-matricula Rules: year 1800..current, acervo 01..99, service 55, book type 1..9, `xx` DV accepted, all-equal rejected, CNS 6th digit by Luhn (empirical, not CNJ-published; office existence not checked)
- [x] feat/32-certidao-matricula Mask with spaces and a hyphen before the DV; unit tests, README, usage (with a Luhn section) and `docs/api/reference.md` in pt-BR
- [ ] Unconfirmed: the DV formula against a real certificate; whether the CNN in force changed it
