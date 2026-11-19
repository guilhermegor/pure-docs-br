"""Apply a caller-supplied display pattern to a bare digit string.

Private to the library: not part of the public API and kept out of ``__all__``. Used by
the documents that have no official mask (CNH, RENAVAM), where the caller picks the
format and the library never presents a made-up one as official.
"""

from __future__ import annotations

from purepii_br._internal.utils.typing import type_checker


_STR_SLOT: str = "N"


@type_checker
def _check_slot_count(str_pattern: str, *, int_len: int) -> None:
    """Raise ``ValueError`` unless the pattern holds exactly ``int_len`` ``N``."""
    int_slots = str_pattern.count(_STR_SLOT)
    if int_slots != int_len:
        msg = f"pattern must contain exactly {int_len} {_STR_SLOT!r}, found {int_slots}"
        raise ValueError(msg)


@type_checker
def apply_mask_pattern(str_digits: str, *, str_pattern: str, int_len: int) -> str:
    """Fill each ``N`` of a pattern with the next digit and copy every other character.

    Parameters
    ----------
    str_digits : str
        The bare unmasked digits.
    str_pattern : str
        The display pattern; ``N`` takes the next digit, anything else is copied as is.
    int_len : int
        The digit count the document must have, and so the ``N`` count the pattern needs.

    Returns
    -------
    str
        The patterned value, or ``str_digits`` unchanged when it is not ``int_len`` long.

    Raises
    ------
    ValueError
        When the pattern does not hold exactly ``int_len`` ``N`` characters.
    """
    _check_slot_count(str_pattern, int_len=int_len)
    if len(str_digits) != int_len:
        return str_digits
    iter_digits = iter(str_digits)
    return "".join(next(iter_digits) if str_c == _STR_SLOT else str_c for str_c in str_pattern)
