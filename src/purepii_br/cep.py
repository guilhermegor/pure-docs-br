"""Brazilian CEP helpers — mask, unmask and validate the postal code.

Pure, stateless functions with the same bad-input contract as
:mod:`purepii_br`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` never raises. A CEP has **no check digit**, so validation is
format only (8 digits); it does not confirm that the CEP exists, which would need the
Correios database. Short numeric values are zero-padded to 8, on purpose, to recover
CEPs that lost the leading zero when stored as numbers (``is_valid_cep("1001000")`` is
``True``). The all-zeros ``00000-000`` passes the format check.
"""

from __future__ import annotations

import re

from purepii_br._internal.utils.float_artifact import _strip_float_artifact
from purepii_br._internal.utils.typing import type_checker


_LEN_CEP: int = 8

_RE_NON_DIGIT: re.Pattern[str] = re.compile(r"\D", re.ASCII)


@type_checker
def unmask_cep(str_value: str) -> str:
    """Normalise a CEP to its bare 8-digit form.

    Parameters
    ----------
    str_value : str
        A CEP in any shape — masked, zero-stripped, or carrying a float ``.0`` tail.

    Returns
    -------
    str
        Digits only, left-zero-padded to 8 when non-empty; empty input (or input with
        no digits) yields ``""``.
    """
    str_clean = _RE_NON_DIGIT.sub("", _strip_float_artifact(str_value))
    if str_clean:
        str_clean = str_clean.zfill(_LEN_CEP)
    return str_clean


@type_checker
def mask_cep(str_value: str) -> str:
    """Format a CEP as ``XXXXX-XXX``.

    Parameters
    ----------
    str_value : str
        A CEP in any shape (it is unmasked first).

    Returns
    -------
    str
        The punctuated CEP when it normalises to 8 digits; otherwise the bare unmasked
        value. That covers empty input and values over 8 digits; a shorter non-empty
        value is never returned, since it is zero-padded to 8.
    """
    str_clean = unmask_cep(str_value)
    if len(str_clean) != _LEN_CEP:
        return str_clean
    return f"{str_clean[:5]}-{str_clean[5:]}"


@type_checker
def is_valid_cep(str_value: str) -> bool:
    """Validate the format of a CEP (8 digits; there is no check digit).

    Parameters
    ----------
    str_value : str
        A CEP in any shape (it is unmasked first).

    Returns
    -------
    bool
        ``True`` when the value normalises to 8 digits. It does not check that the CEP
        exists in the Correios database.
    """
    return len(unmask_cep(str_value)) == _LEN_CEP
