"""Brazilian state registration (Inscricao Estadual, IE) helpers for all 27 UFs.

Pure, stateless functions with the same bad-input contract as
:mod:`pure_docs_br.br_identifiers`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` never raises. The IE does not carry its UF, so every validating
or masking call takes ``str_uf`` as a keyword-only argument. Each UF has its own length,
weights and check-digit rule; the dispatch table below is the single declaration of the
supported UFs (the set of valid UFs is derived from its keys).

A ``str_uf`` that is not one of the 27 acronyms makes :func:`is_valid_inscricao_estadual`
return ``False`` (it never raises), so a mistyped UF makes every IE look invalid.
:func:`mask_inscricao_estadual` with an unknown UF returns the value unmasked.

Sources (the Sintegra formulas page of each UF, ``SINTEGRA`` below meaning
``http://www.sintegra.gov.br/Cad_Estados/cad_<UF>.html``; the index of all UFs is
https://portal.fazenda.sp.gov.br/servicos/icms/Paginas/sintegra-rotina-consistencia.aspx):

* AC, AL, AP, AM, BA, CE, DF, ES, MA, MT, MS, MG, PA, PB, PR, PI, RJ, RN, RS, RO, RR,
  SC, SE, TO: ``SINTEGRA`` with the UF's acronym. The Sintegra pages of DF and RJ publish
  the formula as images (DF: two 800x900 GIFs, RJ: the weights 2,7,6,5,4,3,2).
* SP: https://portal.fazenda.sp.gov.br/servicos/icms/Paginas/sintegra-rotina-consistencia.aspx
  (official example ``110.042.490.114``).
* GO: https://goias.gov.br/economia/roteiro-de-critica-da-inscricao-estadual-de-goias
  (SEFAZ-GO, with the 10103105-10119997 band and the ``11094402`` exception that the
  Sintegra page omits).
* PE: https://www.sintegra.gov.br/Cad_Estados/cad_PE.html (new e-Fisco 9 digits and the
  old CACEPE 14 digits).
* PR: https://www.fazenda.pr.gov.br/Pagina/calculo-digito-verificador

Official examples reproduced by the tests: AC ``01.004.823/001-12``, AL ``24000004``-8,
AP ``030123459``, BA ``123456-63`` and ``612345-57`` (8 digits), ``1000003-06``
(9 digits), CE ``06000001-5``, DF ``073.00001.001-09``, ES ``999999990``, GO
``10.987.654-7``, MA ``12000038-5``, MG ``062.307.904/0081``, MT ``0013000001-9``, PA
``15999999-5`` and ``75000002-3``, PB ``06000001-5``, PE ``0321418-40`` and
``18.1.001.0000004-9``, PI ``012345679``, PR ``123.45678-50``, RN ``20.040.040-1`` and
``20.0.040.040-0``, RO ``101.62521-3`` and ``0000000062521-3``, RR ``24006153-6``, RS
``224/3658792``, SC ``251.040.852``, SE ``27123456-3``, SP ``110.042.490.114``, TO
``29 01 022783 6``. MS and RJ publish no numeric example.

Out of scope: the SP producer-rural ``P-...`` form (any letter makes the value invalid),
the literal ``ISENTO`` (invalid: the caller handles it before calling), and whether the
registration exists or is active.
"""

from __future__ import annotations

from bisect import bisect_left
from collections.abc import Callable
from functools import partial
import re
from typing import NamedTuple

from pure_docs_br._internal.utils.typing import type_checker
from pure_docs_br.br_identifiers import _strip_float_artifact


_INT_MOD_11: int = 11
_INT_MOD_10: int = 10
_INT_MOD_9: int = 9
_INT_GO_BAND_LO: int = 10103105
_INT_GO_BAND_HI: int = 10119997
_INT_AP_RANGE_LIMITS: tuple[int, ...] = (3017000, 3019022)
_TUPLE_AP_P: tuple[int, ...] = (5, 9, 0)
_TUPLE_AP_D: tuple[int, ...] = (0, 1, 0)
_INT_RO_OLD_PREFIX: int = 3
_INT_RO_NEW_LEN: int = 14
_INT_RO_OLD_LEN: int = 9
_STR_MG_ZERO_AT: str = "0"

_RE_NON_DIGIT: re.Pattern[str] = re.compile(r"[^0-9]", re.ASCII)
_RE_LETTER: re.Pattern[str] = re.compile(r"[A-Za-z]", re.ASCII)
_RE_HASH: re.Pattern[str] = re.compile(r"#")

_W9: tuple[int, ...] = (9, 8, 7, 6, 5, 4, 3, 2)
_W10: tuple[int, ...] = (10, *_W9)


class _Step(NamedTuple):
    """One check digit: the weights of its base digits and how a weighted sum maps to it."""

    tuple_weights: tuple[int, ...]
    fn_rule: Callable[[int], int]


class _Variant(NamedTuple):
    """One accepted shape of an IE and the check digits it must carry, in order."""

    re_shape: re.Pattern[str]
    tuple_steps: tuple[_Step, ...]


@type_checker
def _rule_mod11(int_sum: int) -> int:
    """Return ``11 - rest`` where a result of 10 or 11 (rest 1 or 0) becomes 0."""
    return (_INT_MOD_11 - int_sum % _INT_MOD_11) % _INT_MOD_11 % _INT_MOD_10


@type_checker
def _rule_mod11_minus_10(int_sum: int) -> int:
    """Return ``11 - rest`` minus 10 when it exceeds 9 (rest 0 gives 1, rest 1 gives 0)."""
    return (_INT_MOD_11 - int_sum % _INT_MOD_11) % _INT_MOD_10


@type_checker
def _rule_mod10(int_sum: int) -> int:
    """Return ``10 - rest`` where rest 0 gives 0."""
    return (_INT_MOD_10 - int_sum % _INT_MOD_10) % _INT_MOD_10


@type_checker
def _rule_sum_mod11(int_sum: int) -> int:
    """Return the rest of the division by 11, its rightmost digit (SP: 10 gives 0)."""
    return int_sum % _INT_MOD_11 % _INT_MOD_10


@type_checker
def _rule_times10_mod11(int_sum: int) -> int:
    """Return ``(sum * 10)`` mod 11, with 10 as 0 (AL and RN)."""
    return int_sum * _INT_MOD_10 % _INT_MOD_11 % _INT_MOD_10


@type_checker
def _rule_mod9(int_sum: int) -> int:
    """Return the rest of the division by 9 (RR)."""
    return int_sum % _INT_MOD_9


@type_checker
def _rule_am(int_sum: int) -> int:
    """Return the AM digit: ``11 - sum`` below 11 (10 or 11 never match), else mod 11."""
    if int_sum < _INT_MOD_11:
        return _INT_MOD_11 - int_sum
    return _rule_mod11(int_sum)


@type_checker
def _variant(str_pattern: str, *tuple_steps: _Step) -> _Variant:
    """Build a variant from a digits-only regex and its check-digit steps."""
    return _Variant(re.compile(str_pattern, re.ASCII), tuple_steps)


@type_checker
def _sum_weighted(str_base: str, *, tuple_weights: tuple[int, ...]) -> int:
    """Return the sum of each digit of ``str_base`` times its weight."""
    return sum(
        int(str_digit) * int_w for str_digit, int_w in zip(str_base, tuple_weights, strict=True)
    )


@type_checker
def _is_step_ok(str_ie: str, *, cls_step: _Step) -> bool:
    """Check the digit right after the step's base digits against its computed value."""
    int_len = len(cls_step.tuple_weights)
    int_sum = _sum_weighted(str_ie[:int_len], tuple_weights=cls_step.tuple_weights)
    return int(str_ie[int_len]) == cls_step.fn_rule(int_sum)


@type_checker
def _is_variant_ok(str_ie: str, *, cls_variant: _Variant) -> bool:
    """Check the shape of ``str_ie`` and then each of its check digits."""
    if cls_variant.re_shape.fullmatch(str_ie) is None:
        return False
    return all(_is_step_ok(str_ie, cls_step=cls_step) for cls_step in cls_variant.tuple_steps)


@type_checker
def _check_variants(str_ie: str, *, tuple_variants: tuple[_Variant, ...]) -> bool:
    """Check that ``str_ie`` satisfies at least one of the variants."""
    return any(_is_variant_ok(str_ie, cls_variant=cls_v) for cls_v in tuple_variants)


_STEP_MOD11_W9: _Step = _Step(_W9, _rule_mod11)
_VARIANTS_9_DIGITS_MOD11: tuple[_Variant, ...] = (_variant(r"\d{9}", _STEP_MOD11_W9),)

_VARIANTS_AC: tuple[_Variant, ...] = (
    _variant(
        r"01\d{11}",
        _Step((4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2), _rule_mod11),
        _Step((5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2), _rule_mod11),
    ),
)
_VARIANTS_AL: tuple[_Variant, ...] = (
    _variant(r"24[03578]\d{6}", _Step(_W9, _rule_times10_mod11)),
)
_VARIANTS_AM: tuple[_Variant, ...] = (_variant(r"\d{9}", _Step(_W9, _rule_am)),)
_VARIANTS_BA: tuple[_Variant, ...] = (
    _variant(
        r"[0-5,8]\d{7}",
        _Step((7, 6, 5, 4, 3, 2), _rule_mod10),
        _Step((8, 7, 6, 5, 4, 3, 2), _rule_mod10),
    ),
    _variant(
        r"[679]\d{7}",
        _Step((7, 6, 5, 4, 3, 2), _rule_mod11),
        _Step((8, 7, 6, 5, 4, 3, 2), _rule_mod11),
    ),
    _variant(
        r"\d[0-58]\d{7}",
        _Step((8, 7, 6, 5, 4, 3, 2), _rule_mod10),
        _Step((9, 8, 7, 6, 5, 4, 3, 2), _rule_mod10),
    ),
    _variant(
        r"\d[679]\d{7}",
        _Step((8, 7, 6, 5, 4, 3, 2), _rule_mod11),
        _Step((9, 8, 7, 6, 5, 4, 3, 2), _rule_mod11),
    ),
)
_VARIANTS_DF: tuple[_Variant, ...] = (
    _variant(
        r"07\d{11}",
        _Step((4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2), _rule_mod11),
        _Step((5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2), _rule_mod11),
    ),
)
_VARIANTS_GO_EXCEPTION: tuple[_Variant, ...] = (_variant(r"11094402[01]"),)
_VARIANTS_MA: tuple[_Variant, ...] = (_variant(r"12\d{7}", _STEP_MOD11_W9),)
_VARIANTS_MS: tuple[_Variant, ...] = (_variant(r"(?:28|50)\d{7}", _STEP_MOD11_W9),)
_VARIANTS_MT: tuple[_Variant, ...] = (
    _variant(r"\d{11}", _Step((3, 2, 9, 8, 7, 6, 5, 4, 3, 2), _rule_mod11)),
)
_STEP_MG_DV2: _Step = _Step((3, 2, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2), _rule_mod11)
_VARIANTS_MG: tuple[_Variant, ...] = (_variant(r"\d{13}", _STEP_MG_DV2),)
_VARIANTS_PA: tuple[_Variant, ...] = (_variant(r"(?:15|7[5-9])\d{7}", _STEP_MOD11_W9),)
_VARIANTS_PR: tuple[_Variant, ...] = (
    _variant(
        r"\d{10}",
        _Step((3, 2, 7, 6, 5, 4, 3, 2), _rule_mod11),
        _Step((4, 3, 2, 7, 6, 5, 4, 3, 2), _rule_mod11),
    ),
)
_VARIANTS_PE: tuple[_Variant, ...] = (
    _variant(
        r"\d{9}",
        _Step((8, 7, 6, 5, 4, 3, 2), _rule_mod11),
        _Step((9, 8, 7, 6, 5, 4, 3, 2), _rule_mod11),
    ),
    _variant(
        r"\d{14}",
        _Step((5, 4, 3, 2, 1, 9, 8, 7, 6, 5, 4, 3, 2), _rule_mod11_minus_10),
    ),
)
_VARIANTS_RJ: tuple[_Variant, ...] = (
    _variant(r"\d{8}", _Step((2, 7, 6, 5, 4, 3, 2), _rule_mod11)),
)
_VARIANTS_RN: tuple[_Variant, ...] = (
    _variant(r"20\d{7}", _Step(_W9, _rule_times10_mod11)),
    _variant(r"20\d{8}", _Step(_W10, _rule_times10_mod11)),
)
_VARIANTS_RO: tuple[_Variant, ...] = (
    _variant(
        r"\d{14}",
        _Step((6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2), _rule_mod11_minus_10),
    ),
)
_VARIANTS_RR: tuple[_Variant, ...] = (
    _variant(r"24\d{7}", _Step((1, 2, 3, 4, 5, 6, 7, 8), _rule_mod9)),
)
_VARIANTS_RS: tuple[_Variant, ...] = (
    _variant(r"\d{10}", _Step((2, 9, 8, 7, 6, 5, 4, 3, 2), _rule_mod11)),
)
_VARIANTS_SP: tuple[_Variant, ...] = (
    _variant(
        r"\d{12}",
        _Step((1, 3, 4, 5, 6, 7, 8, 10), _rule_sum_mod11),
        _Step((3, 2, 10, 9, 8, 7, 6, 5, 4, 3, 2), _rule_sum_mod11),
    ),
)
_VARIANTS_TO_SHAPE: tuple[_Variant, ...] = (_variant(r"\d{2}(?:01|02|03|99)\d{7}"),)
_VARIANTS_TO_DV: tuple[_Variant, ...] = (_variant(r"\d{9}", _STEP_MOD11_W9),)
_VARIANTS_GO: tuple[_Variant, ...] = (_variant(r"(?:1[015]|2\d)\d{7}"),)


@type_checker
def _compute_go_dv(str_base: str) -> int:
    """Return the GO check digit of 8 digits, with the SEFAZ-GO band for a rest of 1."""
    int_sum = _sum_weighted(str_base, tuple_weights=_W9)
    int_rest = int_sum % _INT_MOD_11
    if int_rest == 1:
        return int(_INT_GO_BAND_LO <= int(str_base) <= _INT_GO_BAND_HI)
    return (_INT_MOD_11 - int_rest) % _INT_MOD_11


@type_checker
def _is_valid_go_rule(str_ie: str) -> bool:
    """Check the prefix, length and weighted check digit of a GO registration."""
    if not _check_variants(str_ie, tuple_variants=_VARIANTS_GO):
        return False
    return int(str_ie[8]) == _compute_go_dv(str_ie[:8])


@type_checker
def _is_valid_go(str_ie: str) -> bool:
    """Validate a GO registration (SEFAZ-GO: weights 9..2, band and 11094402 exception)."""
    return _check_variants(str_ie, tuple_variants=_VARIANTS_GO_EXCEPTION) or _is_valid_go_rule(
        str_ie
    )


@type_checker
def _compute_ap_dv(str_base: str) -> int:
    """Return the AP check digit of 8 digits, using the p and d constants of its range."""
    int_idx = bisect_left(_INT_AP_RANGE_LIMITS, int(str_base))
    int_sum = _TUPLE_AP_P[int_idx] + _sum_weighted(str_base, tuple_weights=_W9)
    int_dv = _INT_MOD_11 - int_sum % _INT_MOD_11
    return _TUPLE_AP_D[int_idx] if int_dv == _INT_MOD_11 else int_dv % _INT_MOD_10


@type_checker
def _is_valid_ap(str_ie: str) -> bool:
    """Validate an AP registration: ``03`` + 6 digits + check digit with p/d ranges."""
    if re.fullmatch(r"03\d{7}", str_ie, re.ASCII) is None:
        return False
    return int(str_ie[8]) == _compute_ap_dv(str_ie[:8])


@type_checker
def _compute_mg_dv1(str_base: str) -> int:
    """Return the MG first check digit: a ``0`` after the city code, weights 1,2 alternating."""
    str_eq = str_base[:3] + _STR_MG_ZERO_AT + str_base[3:]
    int_sum = sum(
        sum(divmod(int(str_digit) * (1 + int_idx % 2), _INT_MOD_10))
        for int_idx, str_digit in enumerate(str_eq)
    )
    return (_INT_MOD_10 - int_sum % _INT_MOD_10) % _INT_MOD_10


@type_checker
def _is_valid_mg(str_ie: str) -> bool:
    """Validate an MG registration (13 digits, two check digits)."""
    if not _check_variants(str_ie, tuple_variants=_VARIANTS_MG):
        return False
    return int(str_ie[11]) == _compute_mg_dv1(str_ie[:11])


@type_checker
def _is_valid_ba(str_ie: str) -> bool:
    """Validate a BA registration (8 or 9 digits, mod 10 or 11 by the leading digits).

    The second check digit (last) is computed first and feeds the first one, so the two
    are swapped before the generic left-to-right check.
    """
    str_swapped = str_ie[:-2] + str_ie[-1:] + str_ie[-2:-1]
    return _check_variants(str_swapped, tuple_variants=_VARIANTS_BA)


@type_checker
def _is_valid_ro(str_ie: str) -> bool:
    """Validate an RO registration: 14 digits, or the pre-2000 9-digit form zero-padded."""
    str_padded = str_ie[_INT_RO_OLD_PREFIX:].zfill(_INT_RO_NEW_LEN)
    return _check_variants(str_ie, tuple_variants=_VARIANTS_RO) or (
        len(str_ie) == _INT_RO_OLD_LEN and _check_variants(str_padded, tuple_variants=_VARIANTS_RO)
    )


@type_checker
def _is_valid_to(str_ie: str) -> bool:
    """Validate a TO registration: the type digits 3 and 4 do not enter the calculation."""
    if not _check_variants(str_ie, tuple_variants=_VARIANTS_TO_SHAPE):
        return False
    return _check_variants(str_ie[:2] + str_ie[4:], tuple_variants=_VARIANTS_TO_DV)


@type_checker
def _is_invalid_uf(str_ie: str) -> bool:  # noqa: ARG001
    """Reject every value (the answer for a UF outside the 27)."""
    return False


_DICT_VALIDATORS: dict[str, Callable[[str], bool]] = {
    "AC": partial(_check_variants, tuple_variants=_VARIANTS_AC),
    "AL": partial(_check_variants, tuple_variants=_VARIANTS_AL),
    "AP": _is_valid_ap,
    "AM": partial(_check_variants, tuple_variants=_VARIANTS_AM),
    "BA": _is_valid_ba,
    "CE": partial(_check_variants, tuple_variants=_VARIANTS_9_DIGITS_MOD11),
    "DF": partial(_check_variants, tuple_variants=_VARIANTS_DF),
    "ES": partial(_check_variants, tuple_variants=_VARIANTS_9_DIGITS_MOD11),
    "GO": _is_valid_go,
    "MA": partial(_check_variants, tuple_variants=_VARIANTS_MA),
    "MT": partial(_check_variants, tuple_variants=_VARIANTS_MT),
    "MS": partial(_check_variants, tuple_variants=_VARIANTS_MS),
    "MG": _is_valid_mg,
    "PA": partial(_check_variants, tuple_variants=_VARIANTS_PA),
    "PB": partial(_check_variants, tuple_variants=_VARIANTS_9_DIGITS_MOD11),
    "PR": partial(_check_variants, tuple_variants=_VARIANTS_PR),
    "PE": partial(_check_variants, tuple_variants=_VARIANTS_PE),
    "PI": partial(_check_variants, tuple_variants=_VARIANTS_9_DIGITS_MOD11),
    "RJ": partial(_check_variants, tuple_variants=_VARIANTS_RJ),
    "RN": partial(_check_variants, tuple_variants=_VARIANTS_RN),
    "RS": partial(_check_variants, tuple_variants=_VARIANTS_RS),
    "RO": _is_valid_ro,
    "RR": partial(_check_variants, tuple_variants=_VARIANTS_RR),
    "SC": partial(_check_variants, tuple_variants=_VARIANTS_9_DIGITS_MOD11),
    "SP": partial(_check_variants, tuple_variants=_VARIANTS_SP),
    "SE": partial(_check_variants, tuple_variants=_VARIANTS_9_DIGITS_MOD11),
    "TO": _is_valid_to,
}

_DICT_MASKS: dict[str, dict[int, str]] = {
    "AC": {13: "##.###.###/###-##"},
    "AL": {9: "##.###.###-#"},
    "AP": {9: "##.###.###-#"},
    "AM": {9: "##.###.###-#"},
    "BA": {8: "######-##", 9: "#######-##"},
    "CE": {9: "########-#"},
    "DF": {13: "###.#####.###-##"},
    "ES": {9: "########-#"},
    "GO": {9: "##.###.###-#"},
    "MA": {9: "##.###.###-#"},
    "MT": {11: "##########-#"},
    "MS": {9: "##.###.###-#"},
    "MG": {13: "###.###.###/####"},
    "PA": {9: "##-######-#"},
    "PB": {9: "########-#"},
    "PR": {10: "###.#####-##"},
    "PE": {9: "#######-##", 14: "##.#.###.#######-#"},
    "PI": {9: "########-#"},
    "RJ": {8: "##.###.##-#"},
    "RN": {9: "##.###.###-#", 10: "##.#.###.###-#"},
    "RS": {10: "###/#######"},
    "RO": {9: "###.#####-#", 14: "#############-#"},
    "RR": {9: "##.###.###-#"},
    "SC": {9: "###.###.###"},
    "SP": {12: "###.###.###.###"},
    "SE": {9: "########-#"},
    "TO": {11: "##.##.######-#"},
}


@type_checker
def unmask_inscricao_estadual(str_value: str) -> str:
    """Normalise a state registration (IE) to its bare digits.

    Parameters
    ----------
    str_value : str
        An IE in any shape: punctuated, spaced or bare. A float ``.0`` tail is dropped
        only from an all-digit value, the one shape a float to str coercion yields; a
        punctuated value was never a float.

    Returns
    -------
    str
        ASCII digits only. Nothing is padded, so a leading zero lost upstream stays lost.
    """
    return _RE_NON_DIGIT.sub("", _strip_float_artifact(str_value))


@type_checker
def mask_inscricao_estadual(str_value: str, *, str_uf: str) -> str:
    """Format a state registration (IE) with the usual mask of its UF.

    Parameters
    ----------
    str_value : str
        An IE in any shape (it is unmasked first).
    str_uf : str
        The two-letter UF acronym, in uppercase.

    Returns
    -------
    str
        The masked IE when the UF is known and the digit count is one of its lengths;
        otherwise the bare unmasked digits. The check digits are not verified.
    """
    str_digits = unmask_inscricao_estadual(str_value)
    str_mask = _DICT_MASKS.get(str_uf, {}).get(len(str_digits))
    if str_mask is None:
        return str_digits
    iter_digits = iter(str_digits)
    return _RE_HASH.sub(lambda _: next(iter_digits), str_mask)


@type_checker
def is_valid_inscricao_estadual(str_value: str, *, str_uf: str) -> bool:
    """Validate a state registration (IE) by the rule of its UF.

    Parameters
    ----------
    str_value : str
        An IE in any shape (it is unmasked first). A value with any letter, such as
        ``ISENTO`` or the SP producer-rural ``P-...`` form, is invalid.
    str_uf : str
        The two-letter UF acronym, in uppercase. A value outside the 27 acronyms (a typo
        included) makes every IE invalid instead of raising.

    Returns
    -------
    bool
        ``True`` when the digit count, prefix and check digits fit the rule of the UF.
        It does not check that the registration exists or is active.
    """
    if _RE_LETTER.search(str_value) is not None:
        return False
    fn_validate = _DICT_VALIDATORS.get(str_uf, _is_invalid_uf)
    return fn_validate(unmask_inscricao_estadual(str_value))
