"""Brazilian CNH (Carteira Nacional de Habilitação) registration number — validate, unmask.

Pure, stateless functions with the same bad-input contract as
:mod:`pure_docs_br.br_identifiers`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` never raises. Only the format is official: Resolução CONTRAN
886/2021, art. 4º, I, gives the registration number 9 characters plus 2 check digits
(11 in all) and says the check digit comes from a modulo 11 routine, without publishing
weights or a formula. **The check-digit algorithm below is NOT official**: it is the
community's reverse-engineered ``dsc`` variant. ``dv1 = sum(d[i] * (9 - i), i=0..8) % 11``
(a value of 10 or more becomes 0 and sets ``dsc = 2``); ``dv2 = sum(d[i] * (i + 1),
i=0..8) % 11 - dsc``, plus 11 when negative and 0 when 10 or more. It can reject a real
CNH and accept an invented number. The CNH has no official mask, so this module ships no
``mask_cnh``; the mask strategy belongs to issue #53.
"""

from __future__ import annotations

import re

from pure_docs_br._internal.utils.typing import type_checker
from pure_docs_br.br_identifiers import _strip_float_artifact


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
        ``""``. There is no ``mask_cnh``: the CNH has no official mask.
    """
    str_digits = _RE_NON_DIGIT.sub("", _strip_float_artifact(str_value))
    return str_digits.zfill(_LEN_CNH) if str_digits else ""


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
