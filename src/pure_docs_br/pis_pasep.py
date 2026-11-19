"""Brazilian PIS/PASEP/NIT/NIS helpers — mask, unmask and validate the 11-digit number.

Pure, stateless functions with the same bad-input contract as
:mod:`pure_docs_br`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` never raises. PIS, PASEP, NIT and NIS are one number under
different names (CAIXA, Banco do Brasil, INSS): 10 base digits plus one check digit,
modulo 11 with weights 3,2,9,8,7,6,5,4,3,2. The modulo 11 is official (DATASUS, CAIXA);
the weights are consensus of public implementations, so confidence is medium. The mask
``XXX.XXXXX.XX-X`` is the usual one. Values of a single repeated digit are rejected, as
in ``is_valid_cpf`` (a proposal pending the owner's decision).
"""

from __future__ import annotations

import re

from pure_docs_br._internal.utils.float_artifact import _strip_float_artifact
from pure_docs_br._internal.utils.typing import type_checker


_LEN_PIS: int = 11
_TUPLE_WEIGHTS: tuple[int, ...] = (3, 2, 9, 8, 7, 6, 5, 4, 3, 2)

_RE_NON_DIGIT: re.Pattern[str] = re.compile(r"\D", re.ASCII)


@type_checker
def _compute_dv(*, str_base: str) -> int:
    """Compute the check digit of the 10 base digits (a result of 10 or more -> 0)."""
    int_sum = sum(
        int(str_d) * int_w for str_d, int_w in zip(str_base, _TUPLE_WEIGHTS, strict=True)
    )
    return (11 - int_sum % 11) % 11 % 10


@type_checker
def unmask_pis_pasep(str_value: str) -> str:
    """Normalise a PIS/PASEP/NIT/NIS to its bare 11-digit form.

    Parameters
    ----------
    str_value : str
        A number in any shape — punctuated, zero-stripped, or carrying a float ``.0``
        tail.

    Returns
    -------
    str
        Digits only, left-zero-padded to 11 when non-empty; empty input (or input with
        no digits) yields ``""``. Values over 11 digits are returned as they are.
    """
    str_clean = _RE_NON_DIGIT.sub("", _strip_float_artifact(str_value))
    if str_clean:
        str_clean = str_clean.zfill(_LEN_PIS)
    return str_clean


@type_checker
def mask_pis_pasep(str_value: str) -> str:
    """Format a PIS/PASEP/NIT/NIS as ``XXX.XXXXX.XX-X``.

    Parameters
    ----------
    str_value : str
        A number in any shape (it is unmasked first).

    Returns
    -------
    str
        The formatted number when it normalises to 11 digits; otherwise the bare
        unmasked value (empty input or more than 11 digits).
    """
    str_clean = unmask_pis_pasep(str_value)
    if len(str_clean) != _LEN_PIS:
        return str_clean
    return f"{str_clean[:3]}.{str_clean[3:8]}.{str_clean[8:10]}-{str_clean[10]}"


@type_checker
def is_valid_pis_pasep(str_value: str) -> bool:
    """Validate a PIS/PASEP/NIT/NIS by its modulo 11 check digit.

    Parameters
    ----------
    str_value : str
        A number in any shape (it is unmasked first).

    Returns
    -------
    bool
        ``True`` when the value has 11 digits, is not a single repeated digit and the
        check digit matches. It does not check that the number was ever issued.
    """
    str_clean = unmask_pis_pasep(str_value)
    if len(str_clean) != _LEN_PIS or len(set(str_clean)) == 1:
        return False
    return str_clean[-1] == str(_compute_dv(str_base=str_clean[:-1]))
