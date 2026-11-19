"""Brazilian vehicle plate (placa) helpers — mask, unmask and validate.

Pure, stateless functions with the same bad-input contract as
:mod:`pure_docs_br`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` never raises. A plate has **no check digit**, so validation is
format only. Two formats are covered: the old ``LLLNNNN`` (CONTRAN 231/2007), written
``ABC-1234``, and the Mercosul ``LLLNLNN`` (CONTRAN 780/2019), written ``ABC1D23``.
Plates with their own formats (armed forces, diplomatic, representation, competition
motorcycles) are out of scope and read as invalid. The check does not consult any
vehicle registry.
"""

from __future__ import annotations

import re

from pure_docs_br._internal.utils.typing import type_checker


_RE_NOT_ALNUM: re.Pattern[str] = re.compile(r"[^A-Za-z0-9]")
_RE_OLD: re.Pattern[str] = re.compile(r"[A-Z]{3}[0-9]{4}")
_RE_MERCOSUL: re.Pattern[str] = re.compile(r"[A-Z]{3}[0-9][A-Z][0-9]{2}")
_RE_PLACA: re.Pattern[str] = re.compile(r"[A-Z]{3}(?:[0-9]{4}|[0-9][A-Z][0-9]{2})")


@type_checker
def unmask_placa(str_value: str) -> str:
    """Normalise a plate to uppercase ``A-Z0-9`` only.

    Parameters
    ----------
    str_value : str
        A plate in any shape — lower case, hyphenated, padded with spaces.

    Returns
    -------
    str
        The upper-cased value with everything outside ASCII ``A-Z0-9`` dropped (full-width
        letters and digits included). No zero padding: a plate is not numeric.
    """
    return _RE_NOT_ALNUM.sub("", str_value).upper()


@type_checker
def mask_placa(str_value: str) -> str:
    """Format a plate: ``ABC-1234`` (old) or ``ABC1D23`` (Mercosul, no separator).

    Parameters
    ----------
    str_value : str
        A plate in any shape (it is unmasked first).

    Returns
    -------
    str
        ``ABC-1234`` for an old-format plate; otherwise the unmasked value, which for a
        Mercosul plate is already its written form.
    """
    str_clean = unmask_placa(str_value)
    if _RE_OLD.fullmatch(str_clean):
        return f"{str_clean[:3]}-{str_clean[3:]}"
    return str_clean


@type_checker
def is_valid_placa(str_value: str) -> bool:
    """Validate the format of a plate, old (``LLLNNNN``) or Mercosul (``LLLNLNN``).

    Parameters
    ----------
    str_value : str
        A plate in any shape (it is unmasked first).

    Returns
    -------
    bool
        ``True`` when the value matches one of the two common formats. It does not check
        that the plate was issued, and special-purpose plates are not covered.
    """
    return _RE_PLACA.fullmatch(unmask_placa(str_value)) is not None
