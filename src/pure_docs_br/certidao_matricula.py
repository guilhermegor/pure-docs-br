"""Brazilian civil certificate matrícula (birth, marriage, death) — validate, mask, unmask.

Pure, stateless functions with the same bad-input contract as
:mod:`pure_docs_br.br_identifiers`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` never raises. One function family covers the three certificate
types, since they share the same 32-digit matrícula.

The structure is official (Provimento CNJ nº 3/2009, kept by the Código Nacional de Normas,
Provimento CNJ nº 149/2023, art. 473): CNS (6), acervo (2), service type (2, always ``55``),
year (4), book type (1), book number (5), sheet (3), entry (7) and 2 check digits. The
check-digit formula is **not** in the regulation (it says the digits are produced by a CNJ
program). The one used here comes from a secondary source that reproduces that program
(ghiorzi.org/DVnew.htm): mod 11 over the first 30 digits (weights ``2..10, 0, 1`` repeating
from 2), then over those 30 plus the first digit (weights starting at 1), remainder 10
becoming 1. It was not checked against a real certificate. A DV of ``xx`` (offices without
a computer, per Provimento 3/2009) is accepted as a valid format.

Rules and where each one comes from:

* Year: ``1800`` to the current year (owner decision, not in the regulation).
* CNS (positions 1-6): the 6th digit must pass Luhn (ISO/IEC 7812-1) over the 6 digits. This
  is an empirical rule (100% of the genuine CNS codes in the CNJ list of serventias pass),
  not one published by the CNJ. Whether the office exists is **not** checked.
* Acervo (positions 7-8): ``01`` to ``99`` (Provimento CNJ nº 237/2026 allows ``02`` or more
  for incorporated offices).
* Book type (position 15): ``1`` to ``9``. The current CNN art. 473 lists 1 to 7; 8 and 9
  come from older certificates, which stay valid.
* All-equal digits are rejected.
"""

from __future__ import annotations

import datetime as dt
import re

from pure_docs_br._internal.utils.typing import type_checker


_LEN_MATRICULA: int = 32
_LEN_PAYLOAD: int = 30
_LEN_CNS: int = 6
_TUPLE_WEIGHTS_DV1: tuple[int, ...] = (
    2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
)  # fmt: skip
_TUPLE_WEIGHTS_DV2: tuple[int, ...] = (1, *_TUPLE_WEIGHTS_DV1[:-1], 9)
_TUPLE_LUHN_DOUBLED: tuple[int, ...] = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)
_INT_MODULUS: int = 11
_INT_YEAR_MIN: int = 1800
_STR_SERVICE_RCPN: str = "55"
_STR_DV_NO_COMPUTER: str = "XX"

_RE_NON_DIGIT: re.Pattern[str] = re.compile(r"\D", re.ASCII)
_RE_KEEP: re.Pattern[str] = re.compile(r"[^0-9Xx]", re.ASCII)
_RE_NO_COMPUTER: re.Pattern[str] = re.compile(r"\d{30}XX", re.ASCII)
_RE_FLOAT_TAIL: re.Pattern[str] = re.compile(r"\s*\.0+\s*$", re.ASCII)
_RE_MASK: re.Pattern[str] = re.compile(
    r"(.{6})(.{2})(.{2})(.{4})(.)(.{5})(.{3})(.{7})(.{2})", re.ASCII
)


@type_checker
def _current_year() -> int:
    """Return the current UTC year (the single clock read, patchable in tests)."""
    return dt.datetime.now(tz=dt.UTC).year


@type_checker
def _strip_float_tail(str_value: str) -> str:
    """Drop a float ``.0`` tail, keeping a ``.00`` that follows 30 digits (the DV pair)."""
    str_head = _RE_FLOAT_TAIL.sub("", str_value)
    int_digits = len(_RE_NON_DIGIT.sub("", str_head))
    is_dv_pair = str_value.rstrip().endswith(".00") and int_digits == _LEN_PAYLOAD
    return str_value.strip() if is_dv_pair else str_head.strip()


@type_checker
def _weighted_dv(str_digits: str, *, tuple_weights: tuple[int, ...]) -> int:
    """Compute one check digit: weighted sum modulo 11, remainder 10 read as 1."""
    list_pairs = zip(str_digits, tuple_weights, strict=True)
    int_remainder = sum(int(str_d) * int_w for str_d, int_w in list_pairs) % _INT_MODULUS
    return int_remainder % 10 + int_remainder // 10


@type_checker
def _compute_dvs(str_payload: str) -> str:
    """Compute the two check digits of a 30-digit payload."""
    int_dv1 = _weighted_dv(str_payload, tuple_weights=_TUPLE_WEIGHTS_DV1)
    int_dv2 = _weighted_dv(str_payload + str(int_dv1), tuple_weights=_TUPLE_WEIGHTS_DV2)
    return f"{int_dv1}{int_dv2}"


@type_checker
def _luhn_ok(str_digits: str) -> bool:
    """Check a digit string with the Luhn algorithm (ISO/IEC 7812-1)."""
    str_reversed = str_digits[::-1]
    int_plain = sum(map(int, str_reversed[0::2]))
    int_doubled = sum(map(_TUPLE_LUHN_DOUBLED.__getitem__, map(int, str_reversed[1::2])))
    return (int_plain + int_doubled) % 10 == 0


@type_checker
def _is_structure_ok(str_value: str) -> bool:
    """Check the CNS, acervo, service, year and book-type fields of a 32-char value."""
    int_year = int(str_value[10:14])
    return (
        _luhn_ok(str_value[:_LEN_CNS])
        and str_value[6:8] != "00"
        and str_value[8:10] == _STR_SERVICE_RCPN
        and _INT_YEAR_MIN <= int_year <= _current_year()
        and str_value[14] != "0"
    )


@type_checker
def _is_dv_ok(str_value: str) -> bool:
    """Check the trailing DVs of a 32-char value; ``XX`` is accepted."""
    set_dvs = {_STR_DV_NO_COMPUTER, _compute_dvs(str_value[:_LEN_PAYLOAD])}
    return str_value[_LEN_PAYLOAD:] in set_dvs


@type_checker
def _pad_digits(str_value: str) -> str:
    """Keep the digits of a value and left-pad them to 32; ``""`` for none or a stray ``X``."""
    str_digits = _RE_NON_DIGIT.sub("", str_value)
    return str_digits.zfill(_LEN_MATRICULA) if str_digits and "X" not in str_value else ""


@type_checker
def unmask_certidao_matricula(str_value: str) -> str:
    """Normalise a certificate matrícula to its bare 32-character form.

    Parameters
    ----------
    str_value : str
        A matrícula in any shape — punctuated, spaced, or carrying a float ``.0`` tail.

    Returns
    -------
    str
        ASCII digits left-padded with zeros to a minimum of 32 (longer input is not
        truncated); 30 digits followed by ``XX`` (the DV of offices without a computer)
        are kept as such, upper-cased. Input with no digits, or with an ``X`` anywhere
        else, yields ``""``.
    """
    str_clean = _RE_KEEP.sub("", _strip_float_tail(str_value)).upper()
    return str_clean if _RE_NO_COMPUTER.fullmatch(str_clean) else _pad_digits(str_clean)


@type_checker
def mask_certidao_matricula(str_value: str) -> str:
    """Format a matrícula as ``NNNNNN NN NN NNNN N NNNNN NNN NNNNNNN-NN``.

    The grouping is spaces, as on the certificate forms (not official).

    Parameters
    ----------
    str_value : str
        A matrícula in any shape (it is unmasked first).

    Returns
    -------
    str
        The spaced matrícula when it normalises to 32 characters; otherwise the bare
        unmasked value.
    """
    str_clean = unmask_certidao_matricula(str_value)
    if len(str_clean) != _LEN_MATRICULA:
        return str_clean
    return _RE_MASK.sub(r"\1 \2 \3 \4 \5 \6 \7 \8-\9", str_clean)


@type_checker
def is_valid_certidao_matricula(str_value: str) -> bool:
    """Validate a birth, marriage or death certificate matrícula.

    The structure is official (Provimento CNJ 3/2009) but the check-digit formula is not
    published; it comes from a secondary source (see the module docstring). The CNS Luhn
    rule is empirical, not published by the CNJ. It does not confirm that the certificate
    exists, was issued, belongs to whoever presents it, or that the office exists.

    Parameters
    ----------
    str_value : str
        A matrícula in any shape (punctuation and a float ``.0`` tail are stripped).

    Returns
    -------
    bool
        ``True`` when the value has 32 positions, is not all-equal digits, the CNS passes
        Luhn, the acervo is ``01``-``99``, the service type is ``55``, the year is
        ``1800`` to the current year, the book type is ``1``-``9`` and the check digits
        match (or are ``xx``).
    """
    str_clean = unmask_certidao_matricula(str_value)
    return (
        len(str_clean) == _LEN_MATRICULA
        and len(set(str_clean)) > 1
        and _is_structure_ok(str_clean)
        and _is_dv_ok(str_clean)
    )
