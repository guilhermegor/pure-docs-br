"""Brazilian utility-bill / tax slip (boleto de arrecadacao) helpers.

Pure, stateless functions with the same bad-input contract as
:mod:`pure_docs_br`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` never raises. Two shapes are accepted: the 44-digit barcode
(product 1, always ``8`` + segment 1 + value id 1 + general DV 1 + 40 more digits) and the
48-digit typeable line (four blocks of 11 digits, each followed by its own DV).

The 3rd digit (value identification) picks the check-digit module for the general DV and for
every block DV: ``6``/``7`` mod 10, ``8``/``9`` mod 11, anything else is invalid. This mod 11
is private to utility-bill slips: a remainder of 0 or 1 gives ``0`` and 10 gives ``1``,
unlike the bank collection slip (cobranca) rule, so it is not shared with that module.

Out of scope: segment, amount, company/agency and telling 47 from 48 digits for the caller.
"""

from __future__ import annotations

from collections.abc import Callable
import re

from pure_docs_br._internal.utils.float_artifact import _strip_float_artifact
from pure_docs_br._internal.utils.typing import type_checker
from pure_docs_br.boleto_cobranca import _compute_mod10


_LEN_BARCODE: int = 44
_LEN_LINE: int = 48
_LEN_BLOCK: int = 11
_INT_BLOCKS: int = 4
_INT_MOD11: int = 11
_INT_WEIGHT_CYCLE: int = 8
_STR_PRODUCT: str = "8"
_INT_NO_MODULE: int = -1
_DICT_MOD11_REMAINDER: dict[int, int] = {0: 0, 1: 0, 10: 1}

_RE_NON_DIGIT: re.Pattern[str] = re.compile(r"[^0-9]", re.ASCII)


@type_checker
def _compute_mod11(str_base: str) -> int:
    """Return the mod 11 digit (weights 2..9 from the right; remainder 0/1 -> 0, 10 -> 1)."""
    int_sum = sum(
        int(str_char) * (int_idx % _INT_WEIGHT_CYCLE + 2)
        for int_idx, str_char in enumerate(reversed(str_base))
    )
    int_rem = int_sum % _INT_MOD11
    return _DICT_MOD11_REMAINDER.get(int_rem, _INT_MOD11 - int_rem)


@type_checker
def _compute_no_module(str_base: str) -> int:
    """Return a digit no check digit can equal, for an unknown value identification."""
    return _INT_NO_MODULE


_DICT_MODULES: dict[str, Callable[[str], int]] = {
    "6": _compute_mod10,
    "7": _compute_mod10,
    "8": _compute_mod11,
    "9": _compute_mod11,
}


@type_checker
def _split_line_blocks(str_line: str) -> list[tuple[str, str]]:
    """Split a 48-digit line into its four (11 digits, DV) blocks."""
    int_size = _LEN_BLOCK + 1
    return [
        (str_line[int_idx : int_idx + _LEN_BLOCK], str_line[int_idx + _LEN_BLOCK])
        for int_idx in range(0, _LEN_LINE, int_size)
    ]


@type_checker
def _is_valid_barcode(str_barcode: str) -> bool:
    """Check product 8, the module-picking 3rd digit and the general DV of 44 digits."""
    fn_compute = _DICT_MODULES.get(str_barcode[2], _compute_no_module)
    str_base = str_barcode[:3] + str_barcode[4:]
    return str_barcode[0] == _STR_PRODUCT and fn_compute(str_base) == int(str_barcode[3])


@type_checker
def _is_valid_line(str_line: str) -> bool:
    """Check every block DV and the barcode rebuilt from the four blocks."""
    fn_compute = _DICT_MODULES.get(str_line[2], _compute_no_module)
    list_blocks = _split_line_blocks(str_line)
    bool_dvs = all(fn_compute(str_base) == int(str_dv) for str_base, str_dv in list_blocks)
    return bool_dvs and _is_valid_barcode("".join(str_base for str_base, _ in list_blocks))


@type_checker
def _reject(str_value: str) -> bool:
    """Reject a value whose length is neither 44 nor 48."""
    return False


_DICT_VALIDATORS: dict[int, Callable[[str], bool]] = {
    _LEN_BARCODE: _is_valid_barcode,
    _LEN_LINE: _is_valid_line,
}


@type_checker
def unmask_boleto_arrecadacao(str_value: str) -> str:
    """Normalise a utility-bill slip to its bare digits.

    Parameters
    ----------
    str_value : str
        A typeable line or barcode, punctuated, spaced or bare. A float ``.0`` tail is
        dropped only from an all-digit value, the one shape a float→str coercion yields.

    Returns
    -------
    str
        ASCII digits only. Nothing is padded.
    """
    return _RE_NON_DIGIT.sub("", _strip_float_artifact(str_value))


@type_checker
def mask_boleto_arrecadacao(str_value: str) -> str:
    """Format a 48-digit typeable line as four ``XXXXXXXXXXX-X`` blocks.

    Parameters
    ----------
    str_value : str
        A line or barcode in any shape (it is unmasked first).

    Returns
    -------
    str
        The line as ``XXXXXXXXXXX-X XXXXXXXXXXX-X XXXXXXXXXXX-X XXXXXXXXXXX-X`` when it
        normalises to 48 digits; otherwise the bare unmasked value (a 44-digit barcode has
        no mask). The hyphen layout is a display convention, not text of the norm.
    """
    str_clean = unmask_boleto_arrecadacao(str_value)
    if len(str_clean) != _LEN_LINE:
        return str_clean
    return " ".join(f"{str_base}-{str_dv}" for str_base, str_dv in _split_line_blocks(str_clean))


@type_checker
def is_valid_boleto_arrecadacao(str_value: str) -> bool:
    """Validate a utility-bill slip barcode (44) or typeable line (48) by its check digits.

    Parameters
    ----------
    str_value : str
        A barcode or line in any shape (it is unmasked first).

    Returns
    -------
    bool
        ``True`` when the digits form a 44-digit barcode starting with 8 whose general DV
        matches, or a 48-digit line whose four block DVs match and whose rebuilt barcode is
        valid. The 3rd digit must be 6 to 9. It does not check segment, amount or company.
    """
    str_clean = unmask_boleto_arrecadacao(str_value)
    return _DICT_VALIDATORS.get(len(str_clean), _reject)(str_clean)
