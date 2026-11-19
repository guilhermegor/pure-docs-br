"""CPF helpers — mask, unmask and validate.

Pure, stateless functions with the bad-input contract documented in :mod:`pure_docs_br`.
``unmask_cpf`` strips punctuation and the spurious ``".0"`` left by a float→str coercion.
Short numeric values are zero-padded before validation, on purpose, to recover identifiers
stored as numbers that lost leading zeros: ``is_valid_cpf("191")`` is ``True`` (it becomes
``00000000191``), while ``"0"`` is rejected as a repeated-digit value.
"""

from __future__ import annotations

import re

from pure_docs_br._internal.utils.float_artifact import _strip_float_artifact
from pure_docs_br._internal.utils.typing import type_checker


_INT_MODULUS = 11
_INT_MIN_REMAINDER = 2

_LEN_CPF: int = 11

_RE_NON_DIGIT: re.Pattern[str] = re.compile(r"\D", re.ASCII)


@type_checker
def unmask_cpf(str_value: str) -> str:
    """Normalise a CPF to its bare 11-digit form.

    Parameters
    ----------
    str_value : str
        A CPF in any shape — masked, zero-stripped, or carrying a float ``.0`` tail.

    Returns
    -------
    str
        Digits only, left-zero-padded to 11 when non-empty; empty input yields ``""``.
    """
    str_clean = _strip_float_artifact(str_value)
    str_clean = _RE_NON_DIGIT.sub("", str_clean)
    if str_clean:
        str_clean = str_clean.zfill(_LEN_CPF)
    return str_clean


@type_checker
def mask_cpf(str_value: str) -> str:
    """Format a CPF as ``XXX.XXX.XXX-XX``.

    Parameters
    ----------
    str_value : str
        A CPF in any shape (it is unmasked first).

    Returns
    -------
    str
        The punctuated CPF when it normalises to 11 digits; otherwise the bare
        unmasked value. That covers empty input and values over 11 digits; a shorter
        non-empty value is never returned, since it is zero-padded to 11.
    """
    str_clean = unmask_cpf(str_value)
    if len(str_clean) != _LEN_CPF:
        return str_clean
    return f"{str_clean[:3]}.{str_clean[3:6]}.{str_clean[6:9]}-{str_clean[9:]}"


@type_checker
def _cpf_check_digit(str_base: str, *, int_start_weight: int) -> int:
    """Compute one CPF check digit via descending mod-11 weighting.

    Parameters
    ----------
    str_base : str
        The base digits the weights apply to (9 for DV1, 10 for DV2).
    int_start_weight : int
        The first (largest) weight; subsequent weights descend by one.

    Returns
    -------
    int
        The check digit (0 when the remainder is below 2, else ``11 - remainder``).
    """
    int_sum = sum(
        int(str_char) * (int_start_weight - int_idx) for int_idx, str_char in enumerate(str_base)
    )
    int_rest = int_sum % 11
    return 0 if int_rest < _INT_MIN_REMAINDER else _INT_MODULUS - int_rest


@type_checker
def is_valid_cpf(str_value: str) -> bool:
    """Validate a CPF's two check digits.

    Parameters
    ----------
    str_value : str
        A CPF in any shape (it is unmasked first).

    Returns
    -------
    bool
        ``True`` when the value normalises to 11 digits whose last two are the correct
        check digits. Repeated-digit values (e.g. all ones) are rejected.
    """
    str_clean = unmask_cpf(str_value)
    return (
        len(str_clean) == _LEN_CPF
        and str_clean.isascii()
        and str_clean.isdigit()
        and len(set(str_clean)) > 1
        and str_clean[9:] == _cpf_check_digits(str_clean)
    )


@type_checker
def _cpf_check_digits(str_clean: str) -> str:
    """Return the two check digits for an 11-digit CPF.

    Parameters
    ----------
    str_clean : str
        An unmasked, 11-digit CPF.

    Returns
    -------
    str
        The two check digits, concatenated.
    """
    int_dv1 = _cpf_check_digit(str_clean[:9], int_start_weight=10)
    int_dv2 = _cpf_check_digit(str_clean[:10], int_start_weight=11)
    return f"{int_dv1}{int_dv2}"
