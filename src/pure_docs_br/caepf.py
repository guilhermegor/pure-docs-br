"""Brazilian CAEPF (Cadastro de Atividade Econômica da Pessoa Física) — validate, mask, unmask.

Pure, stateless functions with the same bad-input contract as
:mod:`pure_docs_br`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` never raises. The structure is official (IN RFB nº 1.828/2018): 14
digits, the first 9 of the holder's CPF, a 3-digit sequential and 2 check digits, masked
``NNN.NNN.NNN/NNN-NN``.

The Receita Federal does not publish the check-digit formula. The one used here is
reconstructed from a community source (ghiorzi.org/DVnew.htm): each digit is
``sum % 11`` (a remainder of 10 becomes 0) with weights ``6,7,8,9,2,3,4,5,6,7,8,9`` over the
12 leading digits, then ``5,6,7,8,9,2,3,4,5,6,7,8,9`` over those 12 plus the first digit;
the two digits read as one number get ``+ 12``, minus 100 when the result passes 99. This
reproduces the official SERPRO sample ``00000002500171`` (Cadastro CAEPF API documentation,
bcadastros.serpro.gov.br/documentacao/cadastro_caepf/) and does not without the ``+ 12``.
Still unconfirmed: the ``> 99`` branch and the remainder-10-as-0 rule. A sequential of
``000`` and an all-equal CPF base are rejected.
"""

from __future__ import annotations

import re

from pure_docs_br._internal.utils.float_artifact import _strip_float_artifact
from pure_docs_br._internal.utils.typing import type_checker


_LEN_CAEPF: int = 14
_LEN_PAYLOAD: int = 12
_LEN_CPF_BASE: int = 9
_TUPLE_WEIGHTS_DV1: tuple[int, ...] = (6, 7, 8, 9, 2, 3, 4, 5, 6, 7, 8, 9)
_TUPLE_WEIGHTS_DV2: tuple[int, ...] = (5, 6, 7, 8, 9, 2, 3, 4, 5, 6, 7, 8, 9)
_INT_MODULUS: int = 11
_INT_DV_OFFSET: int = 12
_INT_DV_WRAP: int = 100
_STR_NO_SEQUENTIAL: str = "000"

_RE_NON_DIGIT: re.Pattern[str] = re.compile(r"\D", re.ASCII)


@type_checker
def _strip_to_digits(str_value: str) -> str:
    """Drop the float ``.0`` tail and every non-ASCII-digit character."""
    return _RE_NON_DIGIT.sub("", _strip_float_artifact(str_value))


@type_checker
def _weighted_digit(str_digits: str, *, tuple_weights: tuple[int, ...]) -> int:
    """Compute one raw check digit: weighted sum modulo 11, remainder 10 read as 0."""
    list_pairs = zip(str_digits, tuple_weights, strict=True)
    int_sum = sum(int(str_d) * int_w for str_d, int_w in list_pairs)
    return int_sum % _INT_MODULUS % 10


@type_checker
def _compute_dvs(str_payload: str) -> str:
    """Compute the two check digits of a 12-digit payload, ``+ 12`` adjustment included."""
    int_dv1 = _weighted_digit(str_payload, tuple_weights=_TUPLE_WEIGHTS_DV1)
    int_dv2 = _weighted_digit(str_payload + str(int_dv1), tuple_weights=_TUPLE_WEIGHTS_DV2)
    int_adjusted = (int_dv1 * 10 + int_dv2 + _INT_DV_OFFSET) % _INT_DV_WRAP
    return f"{int_adjusted:02d}"


@type_checker
def unmask_caepf(str_value: str) -> str:
    """Normalise a CAEPF to its bare 14-digit form.

    Parameters
    ----------
    str_value : str
        A number in any shape — punctuated, spaced, or carrying a float ``.0`` tail.

    Returns
    -------
    str
        ASCII digits only, left-padded with zeros to 14; input with no digits yields ``""``.
    """
    str_digits = _strip_to_digits(str_value)
    return str_digits.zfill(_LEN_CAEPF) if str_digits else ""


@type_checker
def mask_caepf(str_value: str) -> str:
    """Format a CAEPF as ``NNN.NNN.NNN/NNN-NN``.

    Parameters
    ----------
    str_value : str
        A CAEPF in any shape (it is unmasked first).

    Returns
    -------
    str
        The punctuated CAEPF when it normalises to 14 digits; otherwise the bare unmasked
        value (empty input, or more than 14 digits).
    """
    str_clean = unmask_caepf(str_value)
    if len(str_clean) != _LEN_CAEPF:
        return str_clean
    return f"{str_clean[:3]}.{str_clean[3:6]}.{str_clean[6:9]}/{str_clean[9:12]}-{str_clean[12:]}"


@type_checker
def is_valid_caepf(str_value: str) -> bool:
    """Validate a CAEPF by its reconstructed check digits.

    The check-digit formula is not published by the Receita Federal; it reproduces the
    official SERPRO sample ``00000002500171`` but two parts stay unconfirmed (see the
    module docstring). It does not confirm the CAEPF exists, is active or belongs to
    anyone.

    Parameters
    ----------
    str_value : str
        A number in any shape (punctuation and a float ``.0`` tail are stripped).

    Returns
    -------
    bool
        ``True`` when the value, left-padded with zeros to 14 digits like
        :func:`unmask_caepf`, has 14 digits, its CPF base is not all equal, the sequential
        is not ``000`` and the check digits match the computation over the first 12.
    """
    str_digits = unmask_caepf(str_value)
    return (
        len(str_digits) == _LEN_CAEPF
        and len(set(str_digits[:_LEN_CPF_BASE])) > 1
        and str_digits[_LEN_CPF_BASE:_LEN_PAYLOAD] != _STR_NO_SEQUENTIAL
        and str_digits[_LEN_PAYLOAD:] == _compute_dvs(str_digits[:_LEN_PAYLOAD])
    )
