"""Brazilian CNJ unified case number (número único de processo) helpers.

Pure, stateless functions with the same bad-input contract as
:mod:`pure_docs_br.br_identifiers`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` never raises. The number has 20 ASCII digits, written
``NNNNNNN-DD.AAAA.J.TR.OOOO`` (CNJ Resolution 65/2008, art. 1): sequence, check digits,
filing year, justice segment, court, origin unit. The check digits follow ISO 7064 mod
97-10 (Annex VIII): ``int(N AAAA J TR OOOO DD) % 97 == 1``, which is the one-modulus form
of the annex's three-step calculation. ``DD`` runs from 02 to 98, so ``00``, ``01`` and
``99`` are never valid even when the modulus happens to match.

Out of scope: checking ``J`` and ``TR`` against the annex tables, and the per-court
numbering used before Resolution 65/2008. The check does not consult any court.
"""

from __future__ import annotations

import re

from pure_docs_br._internal.utils.typing import type_checker
from pure_docs_br.br_identifiers import _strip_float_artifact


_LEN_PROCESSO: int = 20
_INT_MODULUS: int = 97

_RE_NON_DIGIT: re.Pattern[str] = re.compile(r"\D", re.ASCII)
_RE_SHAPE: re.Pattern[str] = re.compile(r"[0-9]{7}(?:0[2-9]|[1-8][0-9]|9[0-8])[0-9]{11}")


@type_checker
def unmask_processo_cnj(str_value: str) -> str:
    """Normalise a case number to its bare 20-digit form.

    Parameters
    ----------
    str_value : str
        A number in any shape — punctuated, spaced, or carrying a float ``.0`` tail.

    Returns
    -------
    str
        ASCII digits only, left-padded with zeros to 20 (full-width digits are dropped).
        Empty input (or input with no digits) yields ``""``.
    """
    str_clean = _RE_NON_DIGIT.sub("", _strip_float_artifact(str_value))
    return str_clean and str_clean.zfill(_LEN_PROCESSO)


@type_checker
def mask_processo_cnj(str_value: str) -> str:
    """Format a case number as ``NNNNNNN-DD.AAAA.J.TR.OOOO``.

    Parameters
    ----------
    str_value : str
        A number in any shape (it is unmasked first).

    Returns
    -------
    str
        The formatted number when it normalises to 20 digits; otherwise the bare
        unmasked value.
    """
    str_clean = unmask_processo_cnj(str_value)
    if len(str_clean) != _LEN_PROCESSO:
        return str_clean
    return (
        f"{str_clean[:7]}-{str_clean[7:9]}.{str_clean[9:13]}.{str_clean[13]}"
        f".{str_clean[14:16]}.{str_clean[16:]}"
    )


@type_checker
def is_valid_processo_cnj(str_value: str) -> bool:
    """Validate a CNJ case number by its ISO 7064 mod 97-10 check digits.

    Parameters
    ----------
    str_value : str
        A number in any shape (it is unmasked first).

    Returns
    -------
    bool
        ``True`` when the value has 20 digits, ``DD`` is between 02 and 98 and
        ``int(N AAAA J TR OOOO DD) % 97 == 1``. It does not validate the segment or
        court codes, nor that the case exists; pre-2008 numbering is not covered.
    """
    str_clean = unmask_processo_cnj(str_value)
    if _RE_SHAPE.fullmatch(str_clean) is None:
        return False
    return int(str_clean[:7] + str_clean[9:] + str_clean[7:9]) % _INT_MODULUS == 1
