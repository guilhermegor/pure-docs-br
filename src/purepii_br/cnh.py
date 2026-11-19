"""Brazilian CNH (Carteira Nacional de Habilitação) registration number — validate, unmask, mask.

Pure, stateless functions with the same bad-input contract as
:mod:`purepii_br`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` document value never raises (only an invalid ``str_pattern`` in
``mask_*`` raises ``ValueError``). Only the format is official: Resolução CONTRAN
886/2021, art. 4º, I, gives the registration number 9 characters plus 2 check digits
(11 in all) and says the check digit comes from a modulo 11 routine, without publishing
weights or a formula. **The check-digit algorithm below is NOT official**: it is the
community's reverse-engineered ``dsc`` variant. ``dv1 = sum(d[i] * (9 - i), i=0..8) % 11``
(a value of 10 or more becomes 0 and sets ``dsc = 2``); ``dv2 = sum(d[i] * (i + 1),
i=0..8) % 11 - dsc``, plus 11 when negative and 0 when 10 or more. It can reject a real
CNH and accept an invented number. The CNH has no official mask, so ``mask_cnh`` takes the
display pattern from the caller.
"""

from __future__ import annotations

import re

from purepii_br._internal.utils.float_artifact import _strip_float_artifact
from purepii_br._internal.utils.mask_pattern import apply_mask_pattern
from purepii_br._internal.utils.typing import type_checker


_LEN_CNH: int = 11
_LEN_BASE: int = 9
_INT_MODULUS: int = 11
_INT_DV_CEILING: int = 10
_INT_DSC_DISCOUNT: int = 2

_RE_NON_DIGIT: re.Pattern[str] = re.compile(r"\D", re.ASCII)


@type_checker
def _compute_dvs(str_base: str) -> str:
    """Compute the two check digits of a 9-digit base with the ``dsc`` variant."""
    list_d = [int(str_d) for str_d in str_base]
    int_dv1 = sum(int_d * (_LEN_BASE - int_i) for int_i, int_d in enumerate(list_d)) % _INT_MODULUS
    int_dsc = 0
    if int_dv1 >= _INT_DV_CEILING:
        int_dv1, int_dsc = 0, _INT_DSC_DISCOUNT
    int_sum2 = sum(int_d * (int_i + 1) for int_i, int_d in enumerate(list_d))
    int_dv2 = (int_sum2 % _INT_MODULUS - int_dsc) % _INT_MODULUS
    return f"{int_dv1}{0 if int_dv2 >= _INT_DV_CEILING else int_dv2}"


@type_checker
def unmask_cnh(str_value: str) -> str:
    """Normalise a CNH registration number to its bare 11-digit form.

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
    str_digits = _RE_NON_DIGIT.sub("", _strip_float_artifact(str_value))
    return str_digits.zfill(_LEN_CNH) if str_digits else ""


@type_checker
def mask_cnh(str_value: str, *, str_pattern: str) -> str:
    """Format a CNH registration number with a caller-supplied pattern.

    The CNH has no official mask, so the pattern is required and the library imposes none.

    Parameters
    ----------
    str_value : str
        A number in any shape (it is unmasked first).
    str_pattern : str
        The display pattern with exactly 11 ``N``; each takes the next digit and every
        other character is copied as is, e.g. ``"NNN NNNN NNNN"``.

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
    return apply_mask_pattern(unmask_cnh(str_value), str_pattern=str_pattern, int_len=_LEN_CNH)


@type_checker
def is_valid_cnh(str_value: str) -> bool:
    """Validate a CNH registration number with the community ``dsc`` algorithm.

    Format (9 digits + 2 check digits) follows Resolução CONTRAN 886/2021, art. 4º, I;
    the check-digit formula is NOT official and may reject a real CNH or accept an
    invented one. It does not confirm the CNH exists, is current or belongs to anyone.

    Parameters
    ----------
    str_value : str
        A number in any shape (it is unmasked first).

    Returns
    -------
    bool
        ``True`` when the value has 11 digits, they are not all equal, and the two check
        digits match the ``dsc`` computation over the first 9.
    """
    str_clean = unmask_cnh(str_value)
    if len(str_clean) != _LEN_CNH or len(set(str_clean)) == 1:
        return False
    return str_clean[_LEN_BASE:] == _compute_dvs(str_clean[:_LEN_BASE])
