"""Brazilian RG (Registro Geral) and CIN (Carteira de Identidade Nacional) — validate, unmask.

Pure, stateless functions with the same bad-input contract as
:mod:`purepii_br`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` value never raises for the value itself.

There is no national RG norm: each state numbers and validates its own. The routing follows
:mod:`purepii_br.inscricao_estadual`: ``str_uf`` selects a per-UF function from a dict
covering all 27 UFs, matched exactly (uppercase two-letter acronym, no normalisation, so
``"sp"`` is an unknown UF). Differently from the IE, an unknown UF raises ``ValueError``,
and a real UF whose rule is not sourced raises ``NotImplementedError`` — never a silent
``False`` and never an invented rule. Implemented UFs: SP, RJ and MG (see
:func:`is_valid_rg`). No ``mask_rg``: the mask strategy belongs to issue #53.

The CIN number is the CPF (Lei 14.534/2023), so :func:`is_valid_cin` reuses the CPF
validator and has no relation to the RG rules.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
import re

from purepii_br._internal.utils.float_artifact import _strip_float_artifact
from purepii_br._internal.utils.typing import type_checker
from purepii_br.cpf import is_valid_cpf


_INT_BASE_LEN: int = 8
_INT_SP_FULL_LEN: int = 9
_INT_MODULUS_SP: int = 11
_STR_SP_DV_ALPHABET: str = "0123456789X"
_INT_MODULUS_RJ: int = 10
_INT_DIGIT_CAP: int = 9

_RE_PUNCT: re.Pattern[str] = re.compile(r"[\s.\-/]")
_RE_GENERIC: re.Pattern[str] = re.compile(r"[0-9]{6,9}[0-9X]", re.ASCII)
_RE_SP: re.Pattern[str] = re.compile(r"[0-9]{8}[0-9X]?", re.ASCII)
_RE_RJ: re.Pattern[str] = re.compile(r"[0-9]{9}", re.ASCII)
_RE_MG: re.Pattern[str] = re.compile(r"[0-9]{7,8}", re.ASCII)

_TUPLE_UF_UNSOURCED: tuple[str, ...] = (
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "PA", "PB",
    "PR", "PE", "PI", "RN", "RS", "RO", "RR", "SC", "SE", "TO",
)  # fmt: skip


@type_checker
def unmask_rg(str_value: str) -> str:
    """Normalise an RG to its bare form.

    Parameters
    ----------
    str_value : str
        A number in any shape — punctuated (``.``, ``-``, ``/``), spaced, or carrying a
        float ``.0`` tail.

    Returns
    -------
    str
        The value without punctuation or whitespace, uppercased (a trailing ``x`` check
        digit becomes ``X``). Letters are kept, so the validators can reject them. There
        is no ``mask_rg``: the mask strategy belongs to issue #53.
    """
    return _RE_PUNCT.sub("", _strip_float_artifact(str_value)).upper()


@type_checker
def _compute_sp_dv(str_base: str) -> str:
    """Compute the SP check digit of an 8-digit base (modulo 11, weights 9..2, 10 -> X)."""
    list_weights = range(_INT_SP_FULL_LEN, 1, -1)
    int_sum = sum(int(str_d) * int_w for str_d, int_w in zip(str_base, list_weights, strict=True))
    return _STR_SP_DV_ALPHABET[int_sum % _INT_MODULUS_SP]


@type_checker
def _is_valid_sp(str_rg: str) -> bool:
    """SP rule: 9 characters carry the DV, 8 digits are format-only (old documents)."""
    return bool(_RE_SP.fullmatch(str_rg)) and (
        len(str_rg) == _INT_BASE_LEN
        or str_rg[_INT_BASE_LEN:] == _compute_sp_dv(str_rg[:_INT_BASE_LEN])
    )


@type_checker
def _compute_rj_dv(str_base: str) -> int:
    """Compute the RJ check digit (modulo 10, weights 2,1 from the unit digit, nines out)."""
    list_products = [
        int(str_d) * int_w
        for str_d, int_w in zip(reversed(str_base), (2, 1) * _INT_BASE_LEN, strict=False)
    ]
    int_sum = sum(
        int_p - _INT_DIGIT_CAP if int_p > _INT_DIGIT_CAP else int_p for int_p in list_products
    )
    return (_INT_MODULUS_RJ - int_sum % _INT_MODULUS_RJ) % _INT_MODULUS_RJ


@type_checker
def _is_valid_rj(str_rg: str) -> bool:
    """RJ rule: 8 digits plus a modulo-10 check digit (single community source)."""
    return bool(_RE_RJ.fullmatch(str_rg)) and str_rg[_INT_BASE_LEN:] == str(
        _compute_rj_dv(str_rg[:_INT_BASE_LEN])
    )


@type_checker
def _is_valid_mg(str_rg: str) -> bool:
    """MG rule: 7 or 8 digits (a 7-digit TCE-MG record exists), format only."""
    return bool(_RE_MG.fullmatch(str_rg))


@type_checker
def _is_valid_generic(str_rg: str) -> bool:
    """Heuristic used without a UF: 7 to 10 characters, ``X`` only as the last."""
    return bool(_RE_GENERIC.fullmatch(str_rg))


@type_checker
def _raise_unsourced(str_rg: str, *, str_uf: str) -> bool:
    """Refuse a UF whose rule has no cited source."""
    msg = f"no sourced RG rule for UF {str_uf!r}; value {str_rg!r} was not validated"
    raise NotImplementedError(msg)


_DICT_VALIDATORS: dict[str, Callable[[str], bool]] = {
    "SP": _is_valid_sp,
    "RJ": _is_valid_rj,
    "MG": _is_valid_mg,
    **{str_uf: partial(_raise_unsourced, str_uf=str_uf) for str_uf in _TUPLE_UF_UNSOURCED},
}


_DICT_ROUTES: dict[str | None, Callable[[str], bool]] = {
    None: _is_valid_generic,
    **{str_uf: fn_rule for str_uf, fn_rule in _DICT_VALIDATORS.items()},  # noqa: C416
}


@type_checker
def _get_validator(str_uf: str | None) -> Callable[[str], bool]:
    """Pick the validator for a UF; ``None`` selects the generic heuristic."""
    if str_uf not in _DICT_ROUTES:
        msg = f"unknown UF {str_uf!r}; expected an uppercase two-letter acronym"
        raise ValueError(msg)
    return _DICT_ROUTES[str_uf]


@type_checker
def is_valid_rg(str_value: str, *, str_uf: str | None = None) -> bool:
    """Validate an RG by the rule of its issuing UF.

    There is no national RG norm. ``str_uf`` is matched exactly (uppercase acronym, no
    normalisation). Rules:

    - **SP**: 9 characters, DV modulo 11 with weights 9..2 over the 8-digit base, remainder
      10 written ``X`` (reconstructed by the community, not published by SSP-SP; three
      agreeing community sources). 8 digits are accepted as format only, since old
      documents carry no DV.
    - **RJ**: 9 digits, DV modulo 10 with weights 2,1 from the unit digit and nines out.
      Community rule from a **single source** (ghiorzi.org), low confidence.
    - **MG**: 7 or 8 digits, format only (MG has no DV; a TCE-MG record shows a 7-digit RG).
    - **Any other UF**: ``NotImplementedError`` (no sourced rule yet).
    - **No UF**: 7 to 10 characters, digits only, ``X`` allowed only last. A heuristic,
      not a norm; it can reject documents with letter prefixes.

    It does not confirm the RG exists, belongs to the holder or was issued by that UF.
    For the CIN use :func:`is_valid_cin`.

    Parameters
    ----------
    str_value : str
        An RG in any shape (punctuation and a float ``.0`` tail are stripped).
    str_uf : str or None, optional
        Uppercase two-letter UF acronym, or ``None`` for the generic heuristic.

    Returns
    -------
    bool
        Whether the value satisfies the UF's rule.

    Raises
    ------
    ValueError
        When ``str_uf`` is not one of the 27 UF acronyms.
    NotImplementedError
        When ``str_uf`` is a UF with no sourced rule.
    """
    return _get_validator(str_uf)(unmask_rg(str_value))


@type_checker
def is_valid_cin(str_value: str) -> bool:
    """Validate a CIN number, which is the holder's CPF (Lei 14.534/2023).

    Parameters
    ----------
    str_value : str
        A CPF in any shape; the rule is exactly :func:`purepii_br.is_valid_cpf`.

    Returns
    -------
    bool
        ``True`` when the value is a valid CPF. Unrelated to :func:`is_valid_rg`.
    """
    return is_valid_cpf(str_value)
