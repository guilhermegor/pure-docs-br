"""Brazilian electronic fiscal document access key (chave de acesso) helpers.

Pure, stateless functions with the same bad-input contract as
:mod:`purepii_br`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` never raises. The key has 44 characters shared by NF-e, NFC-e, CT-e
and MDF-e: ``cUF`` (2) + ``AAMM`` (4) + issuer CNPJ (14) + ``mod`` (2) + series (3) +
number (9) + ``tpEmis`` (1) + ``cNF`` (8) + ``cDV`` (1) (MOC 7.0, item 2.2.6.2).

Since the joint technical note NT 2025.001 (alphanumeric CNPJ) the first 12 characters of
the embedded CNPJ, key positions 7 to 18, may be the letters ``A``-``Z``; every other
position stays a digit (shape ``[0-9]{6}[A-Z0-9]{12}[0-9]{26}``). The check digit is the
mod 11 of the 43 leading characters, each worth ``ord(char) - 48``, weighted 2..9 from the
right; a remainder of 0 or 1 gives ``0``. For all-digit keys this equals the MOC 7.0 rule.

Out of scope: validating the embedded CNPJ, ``cUF`` against the IBGE table and ``mod``.
"""

from __future__ import annotations

import re

from purepii_br._internal.utils.float_artifact import _strip_float_artifact
from purepii_br._internal.utils.typing import type_checker


_LEN_CHAVE: int = 44
_LEN_GROUP: int = 4
_INT_ASCII_ZERO: int = 48
_INT_MODULUS: int = 11
_INT_WEIGHT_CYCLE: int = 8
_INT_MIN_REST: int = 2

_RE_PREFIX: re.Pattern[str] = re.compile(r"^(?:NFe|CTe|MDFe)", re.ASCII | re.IGNORECASE)
_RE_NON_ALNUM: re.Pattern[str] = re.compile(r"[^0-9A-Za-z]", re.ASCII)
_RE_SHAPE: re.Pattern[str] = re.compile(r"[0-9]{6}[A-Z0-9]{12}[0-9]{26}")


@type_checker
def _compute_dv(str_base: str) -> int:
    """Return the check digit of the 43 leading characters of a key."""
    int_sum = sum(
        (ord(str_char) - _INT_ASCII_ZERO) * (int_idx % _INT_WEIGHT_CYCLE + 2)
        for int_idx, str_char in enumerate(reversed(str_base))
    )
    int_rest = int_sum % _INT_MODULUS
    return 0 if int_rest < _INT_MIN_REST else _INT_MODULUS - int_rest


@type_checker
def unmask_chave_acesso(str_value: str) -> str:
    """Normalise an access key to its bare 44-character form.

    Parameters
    ----------
    str_value : str
        A key in any shape: spaced, punctuated, with the XML ``Id`` prefix (``NFe``,
        ``CTe`` or ``MDFe``) or carrying a float ``.0`` tail.

    Returns
    -------
    str
        ASCII digits and uppercase letters ``A``-``Z`` only. Nothing is padded.
    """
    str_clean = _RE_PREFIX.sub("", _strip_float_artifact(str_value))
    return _RE_NON_ALNUM.sub("", str_clean).upper()


@type_checker
def mask_chave_acesso(str_value: str) -> str:
    """Format an access key as 11 groups of 4 characters, as printed on the DANFE.

    Parameters
    ----------
    str_value : str
        A key in any shape (it is unmasked first).

    Returns
    -------
    str
        The spaced key when it normalises to 44 characters; otherwise the bare unmasked
        value.
    """
    str_clean = unmask_chave_acesso(str_value)
    if len(str_clean) != _LEN_CHAVE:
        return str_clean
    return " ".join(str_clean[i : i + _LEN_GROUP] for i in range(0, _LEN_CHAVE, _LEN_GROUP))


@type_checker
def is_valid_chave_acesso(str_value: str) -> bool:
    """Validate an access key by its shape and mod 11 check digit.

    Parameters
    ----------
    str_value : str
        A key in any shape (it is unmasked first).

    Returns
    -------
    bool
        ``True`` when the value has 44 characters in the shape
        ``[0-9]{6}[A-Z0-9]{12}[0-9]{26}`` and the last digit matches the check digit of
        the first 43. It does not validate the embedded CNPJ, ``cUF`` or ``mod``, nor that
        the document exists.
    """
    str_clean = unmask_chave_acesso(str_value)
    if _RE_SHAPE.fullmatch(str_clean) is None:
        return False
    return _compute_dv(str_clean[:-1]) == int(str_clean[-1])
