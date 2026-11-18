"""Brazilian Título de Eleitor helpers — mask, unmask and validate the voter ID.

Pure, stateless functions with the same bad-input contract as
:mod:`pure_docs_br`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` never raises. A title has 12 digits: 8 sequential, 2 for the
state (UF) and 2 check digits, both modulo 11. The algorithm comes from the Portuguese
Wikipedia article "Título de eleitor" (secondary source); the CAIXA *Guia de
Qualificação Cadastral* only corroborates that the check is modulo 11. The TSE does not
publish the formula, so confidence is medium. The mask ``XXXX XXXX XXXX`` is a proposal,
not an official format. Legacy 13-digit titles (SP/MG) are out of scope and invalid.
"""

from __future__ import annotations

import re

from pure_docs_br._internal.utils.float_artifact import _strip_float_artifact
from pure_docs_br._internal.utils.typing import type_checker


_LEN_TITULO: int = 12
_LEN_SEQ: int = 8
_UF_MIN: int = 1
_UF_MAX: int = 28
_SET_UF_SP_MG: frozenset[int] = frozenset({1, 2})

_RE_NON_DIGIT: re.Pattern[str] = re.compile(r"\D", re.ASCII)


@type_checker
def _compute_dv(*, int_sum: int, int_uf: int) -> int:
    """Reduce a weighted sum to a check digit (10 -> 0; SP/MG 0 -> 1)."""
    int_rest = int_sum % 11
    int_zero_as = int(int_uf in _SET_UF_SP_MG)
    return {10: 0, 0: int_zero_as}.get(int_rest, int_rest)


@type_checker
def _check_digits_match(*, str_clean: str) -> bool:
    """Compare both check digits of a 12-digit title with the computed ones."""
    int_uf = int(str_clean[_LEN_SEQ : _LEN_SEQ + 2])
    if not _UF_MIN <= int_uf <= _UF_MAX:
        return False
    int_sum_1 = sum(
        int(str_d) * int_w for str_d, int_w in zip(str_clean[:_LEN_SEQ], range(2, 10), strict=True)
    )
    int_dv1 = _compute_dv(int_sum=int_sum_1, int_uf=int_uf)
    int_sum_2 = int(str_clean[8]) * 7 + int(str_clean[9]) * 8 + int_dv1 * 9
    int_dv2 = _compute_dv(int_sum=int_sum_2, int_uf=int_uf)
    return str_clean[10:] == f"{int_dv1}{int_dv2}"


@type_checker
def unmask_titulo_eleitor(str_value: str) -> str:
    """Normalise a Título de Eleitor to its bare 12-digit form.

    Parameters
    ----------
    str_value : str
        A title in any shape — spaced, punctuated, zero-stripped, or carrying a float
        ``.0`` tail.

    Returns
    -------
    str
        Digits only, left-zero-padded to 12 when non-empty; empty input (or input with
        no digits) yields ``""``. Values over 12 digits are returned as they are.
    """
    str_clean = _RE_NON_DIGIT.sub("", _strip_float_artifact(str_value))
    if str_clean:
        str_clean = str_clean.zfill(_LEN_TITULO)
    return str_clean


@type_checker
def mask_titulo_eleitor(str_value: str) -> str:
    """Format a Título de Eleitor as ``XXXX XXXX XXXX``.

    Parameters
    ----------
    str_value : str
        A title in any shape (it is unmasked first).

    Returns
    -------
    str
        The grouped title when it normalises to 12 digits; otherwise the bare unmasked
        value (empty input or more than 12 digits).
    """
    str_clean = unmask_titulo_eleitor(str_value)
    if len(str_clean) != _LEN_TITULO:
        return str_clean
    return f"{str_clean[:4]} {str_clean[4:8]} {str_clean[8:]}"


@type_checker
def is_valid_titulo_eleitor(str_value: str) -> bool:
    """Validate a Título de Eleitor by UF code and both check digits.

    Parameters
    ----------
    str_value : str
        A title in any shape (it is unmasked first).

    Returns
    -------
    bool
        ``True`` when the value has 12 digits, a UF code from 01 to 28 and both modulo
        11 check digits match. It does not check that the title was ever issued.
    """
    str_clean = unmask_titulo_eleitor(str_value)
    if len(str_clean) != _LEN_TITULO:
        return False
    return _check_digits_match(str_clean=str_clean)
