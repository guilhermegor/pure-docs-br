"""Brazilian RENAVAM (Registro Nacional de Veículos Automotores) — validate, unmask, mask.

Pure, stateless functions with the same bad-input contract as
:mod:`pure_docs_br.br_identifiers`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` document value never raises (only an invalid ``str_pattern`` in
``mask_*`` raises ``ValueError``). The check-digit calculation follows Siscomex,
Comunicado de Importação nº 064/2025 ("algoritmo módulo 11 e peso 9"): over the first
10 digits, weights ``3,2,9,8,7,6,5,4,3,2`` left to right; ``rest = sum % 11``; the check
digit is 0 when ``rest`` is 0 or 1, else ``11 - rest``. SENATRAN/DENATRAN never published
a complete RENAVAM specification, and these parts are community convention, not official:
accepting the old 9-digit number by left-padding with zeros to 11, and rejecting an
all-equal number. The RENAVAM has no official mask, so ``mask_renavam`` takes
the display pattern from the caller.
"""

from __future__ import annotations

import re

from pure_docs_br._internal.utils.mask_pattern import apply_mask_pattern
from pure_docs_br._internal.utils.typing import type_checker
from pure_docs_br.br_identifiers import _strip_float_artifact


_LEN_RENAVAM: int = 11
_LEN_LEGACY: int = 9
_LEN_BASE: int = 10
_TUPLE_WEIGHTS: tuple[int, ...] = (3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_INT_MODULUS: int = 11
_INT_REST_FLOOR: int = 2

_RE_NON_DIGIT: re.Pattern[str] = re.compile(r"\D", re.ASCII)


@type_checker
def _strip_to_digits(str_value: str) -> str:
    """Drop the float ``.0`` tail and every non-ASCII-digit character."""
    return _RE_NON_DIGIT.sub("", _strip_float_artifact(str_value))


@type_checker
def _compute_dv(str_base: str) -> str:
    """Compute the check digit of a 10-digit base (Siscomex modulo 11, weights 3..2)."""
    list_pairs = zip(str_base, _TUPLE_WEIGHTS, strict=True)
    int_sum = sum(int(str_d) * int_w for str_d, int_w in list_pairs)
    int_rest = int_sum % _INT_MODULUS
    return str(0 if int_rest < _INT_REST_FLOOR else _INT_MODULUS - int_rest)


@type_checker
def unmask_renavam(str_value: str) -> str:
    """Normalise a RENAVAM to its bare 11-digit form.

    Parameters
    ----------
    str_value : str
        A number in any shape — punctuated, spaced, or carrying a float ``.0`` tail.

    Returns
    -------
    str
        ASCII digits only, left-padded with zeros to 11; input with no digits yields
        ``""``.
    """
    str_digits = _strip_to_digits(str_value)
    return str_digits.zfill(_LEN_RENAVAM) if str_digits else ""


@type_checker
def mask_renavam(str_value: str, *, str_pattern: str) -> str:
    """Format a RENAVAM with a caller-supplied pattern.

    The RENAVAM has no official mask, so the pattern is required and the library imposes
    none.

    Parameters
    ----------
    str_value : str
        A number in any shape (it is unmasked first; 9 digits are padded to 11).
    str_pattern : str
        The display pattern with exactly 11 ``N``; each takes the next digit and every
        other character is copied as is, e.g. ``"NNNNNNNNNN-N"``.

    Returns
    -------
    str
        The patterned number when it normalises to 11 digits; otherwise the bare unmasked
        value (empty input, or more than 11 digits).

    Raises
    ------
    ValueError
        When the pattern does not contain exactly 11 ``N``.
    """
    str_clean = unmask_renavam(str_value)
    return apply_mask_pattern(str_clean, str_pattern=str_pattern, int_len=_LEN_RENAVAM)


@type_checker
def is_valid_renavam(str_value: str) -> bool:
    """Validate a RENAVAM by its check digit.

    The check digit follows Siscomex, Comunicado de Importação nº 064/2025. Accepting the
    old 9-digit number (padded with zeros to 11) and rejecting an all-equal number are
    community conventions, not SENATRAN rules. It does not confirm the vehicle exists,
    is active or belongs to anyone.

    Parameters
    ----------
    str_value : str
        A number in any shape (punctuation and a float ``.0`` tail are stripped).

    Returns
    -------
    bool
        ``True`` when the value has 9 or 11 digits, the 11-digit form is not all equal
        and its check digit matches the computation over the first 10.
    """
    str_digits = _strip_to_digits(str_value)
    str_clean = str_digits.zfill(_LEN_RENAVAM)
    return (
        len(str_digits) in {_LEN_LEGACY, _LEN_RENAVAM}
        and len(set(str_clean)) > 1
        and str_clean[_LEN_BASE:] == _compute_dv(str_clean[:_LEN_BASE])
    )
