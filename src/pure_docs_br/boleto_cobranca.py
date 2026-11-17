"""Brazilian bank collection slip (boleto de cobranca) helpers.

Pure, stateless functions with the same bad-input contract as
:mod:`pure_docs_br.br_identifiers`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` never raises. Two shapes are accepted: the 44-digit barcode
(bank 3 + currency 1 + general DV 1 + due-date factor 4 + amount 10 + free field 25) and
the 47-digit typeable line (``AAABC.CCCCX DDDDD.DDDDDY EEEEE.EEEEEZ K UUUUVVVVVVVVVV``).

Fields 1 to 3 of the line carry a mod 10 check digit. The general DV (barcode position 5,
``K`` in the line) is the mod 11 of the other 43 digits weighted 2..9 from the right,
where a result of 0, 10 or 11 gives ``1``. This mod 11 is private to collection slips:
utility-bill (arrecadacao, 48 digits) slips use a different rule, so it is not shared.

Out of scope: the due-date factor, the amount, whether the bank exists and converting a
line to a barcode for the caller.
"""

from __future__ import annotations

from collections.abc import Callable
import re

from pure_docs_br._internal.utils.typing import type_checker
from pure_docs_br.br_identifiers import _strip_float_artifact


_LEN_BARCODE: int = 44
_LEN_LINE: int = 47
_INT_MOD10: int = 10
_INT_MOD11: int = 11
_INT_WEIGHT_CYCLE: int = 8
_INT_GENERAL_DV_FALLBACK: int = 1

_RE_NON_DIGIT: re.Pattern[str] = re.compile(r"[^0-9]", re.ASCII)


@type_checker
def _compute_mod10(str_base: str) -> int:
    """Return the mod 10 check digit (weights 2,1,2,1... from the right, digit sums)."""
    int_sum = sum(
        sum(divmod(int(str_char) * (2 - int_idx % 2), _INT_MOD10))
        for int_idx, str_char in enumerate(reversed(str_base))
    )
    return (_INT_MOD10 - int_sum % _INT_MOD10) % _INT_MOD10


@type_checker
def _compute_general_dv(str_base: str) -> int:
    """Return the general DV of the 43 digits left after dropping barcode position 5."""
    int_sum = sum(
        int(str_char) * (int_idx % _INT_WEIGHT_CYCLE + 2)
        for int_idx, str_char in enumerate(reversed(str_base))
    )
    int_dv = _INT_MOD11 - int_sum % _INT_MOD11
    return _INT_GENERAL_DV_FALLBACK if int_dv in {0, 10, 11} else int_dv


@type_checker
def _convert_line_to_barcode(str_line: str) -> str:
    """Rebuild the 44-digit barcode from a 47-digit typeable line."""
    return (
        str_line[0:4]
        + str_line[32]
        + str_line[33:47]
        + str_line[4:9]
        + str_line[10:20]
        + str_line[21:31]
    )


@type_checker
def _is_valid_barcode(str_barcode: str) -> bool:
    """Check the general DV of a 44-digit barcode."""
    return _compute_general_dv(str_barcode[:4] + str_barcode[5:]) == int(str_barcode[4])


@type_checker
def _has_valid_field_dvs(str_line: str) -> bool:
    """Check the mod 10 digit of fields 1 to 3 of a 47-digit line."""
    list_fields = [(str_line[0:9], str_line[9]), (str_line[10:20], str_line[20])]
    list_fields.append((str_line[21:31], str_line[31]))
    return all(_compute_mod10(str_base) == int(str_dv) for str_base, str_dv in list_fields)


@type_checker
def _is_valid_line(str_line: str) -> bool:
    """Check the field digits and the general DV of a 47-digit line."""
    return _has_valid_field_dvs(str_line) and _is_valid_barcode(_convert_line_to_barcode(str_line))


@type_checker
def _reject(str_value: str) -> bool:
    """Reject a value whose length is neither 44 nor 47."""
    return False


_DICT_VALIDATORS: dict[int, Callable[[str], bool]] = {
    _LEN_BARCODE: _is_valid_barcode,
    _LEN_LINE: _is_valid_line,
}


@type_checker
def unmask_boleto_cobranca(str_value: str) -> str:
    """Normalise a collection slip to its bare digits.

    Parameters
    ----------
    str_value : str
        A typeable line or barcode in any shape: punctuated, spaced or carrying a float
        ``.0`` tail.

    Returns
    -------
    str
        ASCII digits only. Nothing is padded.
    """
    return _RE_NON_DIGIT.sub("", _strip_float_artifact(str_value))


@type_checker
def mask_boleto_cobranca(str_value: str) -> str:
    """Format a 47-digit typeable line as ``AAAAA.AAAAA BBBBB.BBBBBB CCCCC.CCCCCC D E``.

    Parameters
    ----------
    str_value : str
        A line or barcode in any shape (it is unmasked first).

    Returns
    -------
    str
        The formatted line when it normalises to 47 digits; otherwise the bare unmasked
        value (a 44-digit barcode has no mask).
    """
    str_clean = unmask_boleto_cobranca(str_value)
    if len(str_clean) != _LEN_LINE:
        return str_clean
    return (
        f"{str_clean[0:5]}.{str_clean[5:10]} {str_clean[10:15]}.{str_clean[15:21]} "
        f"{str_clean[21:26]}.{str_clean[26:32]} {str_clean[32]} {str_clean[33:]}"
    )


@type_checker
def is_valid_boleto_cobranca(str_value: str) -> bool:
    """Validate a collection slip barcode (44) or typeable line (47) by its check digits.

    Parameters
    ----------
    str_value : str
        A barcode or line in any shape (it is unmasked first).

    Returns
    -------
    bool
        ``True`` when the digits form a 44-digit barcode with a correct general DV, or a
        47-digit line whose three field digits (mod 10) and general DV (mod 11) all match.
        It does not check the due-date factor, the amount or that the bank exists.
    """
    str_clean = unmask_boleto_cobranca(str_value)
    return _DICT_VALIDATORS.get(len(str_clean), _reject)(str_clean)
