"""Brazilian CNS (Cartão Nacional de Saúde) helpers — mask, unmask and validate.

Pure, stateless functions with the same bad-input contract as
:mod:`pure_docs_br`: a non-``str`` raises ``TypeError`` from the runtime
type checker, a ``str`` never raises. The CNS has 15 ASCII digits and the first one sets
the kind. ``1``/``2`` are definitive: the number is ``PIS(11) + suffix(3) + dv(1)``, with
``dv = 11 - (sum(d[i] * (15 - i), i=0..10) % 11)`` (11 becomes 0); a ``dv`` of 10 adds 2 to
the sum, recomputes the ``dv`` and fixes the suffix at ``001`` (otherwise ``000``).
``7``/``8``/``9`` are provisional: ``sum(d[i] * (15 - i), i=0..14)`` must be divisible by
11. A first digit of ``0``, ``3``, ``4``, ``5`` or ``6`` is invalid. Source: the DATASUS
routines ``validaCns`` and ``validaCnsProv`` as published by the Ministry of Health in the
e-SUS APS integration layout, "Validar CNS"
(https://integracao.esusab.ufsc.br/ledi/documentacao/regras/algoritmo_CNS.html); both
branches above follow them line for line. That page also accepts a provisional number
starting with ``5``; this module rejects it, as issue #16 specifies, pending the owner's
decision. The mask ``XXX XXXX XXXX XXXX`` is a proposal (the CNS has no official mask), pending the
owner's decision. No CNS starts with 0, so ``unmask_cns`` never pads zeros.
"""

from __future__ import annotations

from collections.abc import Callable
import re

from pure_docs_br._internal.utils.float_artifact import _strip_float_artifact
from pure_docs_br._internal.utils.typing import type_checker


_LEN_CNS: int = 15
_LEN_PIS_BASE: int = 11
_INT_DV_NEEDS_SUFFIX: int = 10

_RE_NON_DIGIT: re.Pattern[str] = re.compile(r"\D", re.ASCII)


@type_checker
def _weighted_sum(*, str_digits: str) -> int:
    """Sum each digit times its weight, counting down from 15."""
    return sum(int(str_d) * (_LEN_CNS - int_i) for int_i, str_d in enumerate(str_digits))


@type_checker
def _is_valid_definitive(str_cns: str) -> bool:
    """Check a CNS starting with 1 or 2 against ``base11 + suffix + dv``."""
    str_base = str_cns[:_LEN_PIS_BASE]
    int_sum = _weighted_sum(str_digits=str_base)
    int_dv = (11 - int_sum % 11) % 11
    str_suffix = "000"
    if int_dv == _INT_DV_NEEDS_SUFFIX:
        int_dv = 11 - (int_sum + 2) % 11
        str_suffix = "001"
    return str_cns == f"{str_base}{str_suffix}{int_dv}"


@type_checker
def _is_valid_provisional(str_cns: str) -> bool:
    """Check a CNS starting with 7, 8 or 9: the weighted sum divides by 11."""
    return _weighted_sum(str_digits=str_cns) % 11 == 0


_DICT_VALIDATORS: dict[str, Callable[[str], bool]] = {
    "1": _is_valid_definitive,
    "2": _is_valid_definitive,
    "7": _is_valid_provisional,
    "8": _is_valid_provisional,
    "9": _is_valid_provisional,
}


@type_checker
def unmask_cns(str_value: str) -> str:
    """Normalise a CNS to its bare 15-digit form.

    Parameters
    ----------
    str_value : str
        A number in any shape — punctuated, spaced, or carrying a float ``.0`` tail.

    Returns
    -------
    str
        ASCII digits only; empty input (or input with no digits) yields ``""``. Zeros are
        never padded, because no valid CNS starts with 0.
    """
    return _RE_NON_DIGIT.sub("", _strip_float_artifact(str_value))


@type_checker
def mask_cns(str_value: str) -> str:
    """Format a CNS as ``XXX XXXX XXXX XXXX``.

    Parameters
    ----------
    str_value : str
        A number in any shape (it is unmasked first).

    Returns
    -------
    str
        The formatted number when it normalises to 15 digits; otherwise the bare
        unmasked value. The mask is a library convention, not an official one.
    """
    str_clean = unmask_cns(str_value)
    if len(str_clean) != _LEN_CNS:
        return str_clean
    return f"{str_clean[:3]} {str_clean[3:7]} {str_clean[7:11]} {str_clean[11:]}"


@type_checker
def is_valid_cns(str_value: str) -> bool:
    """Validate a CNS (definitive or provisional) by its modulo 11 rule.

    Parameters
    ----------
    str_value : str
        A number in any shape (it is unmasked first).

    Returns
    -------
    bool
        ``True`` when the value has 15 digits and satisfies the rule of its kind: the
        definitive (first digit 1 or 2) check digit and suffix, or the provisional
        (7, 8 or 9) sum divisible by 11. It does not check that the card was ever issued.
    """
    str_clean = unmask_cns(str_value)
    fn_rule = _DICT_VALIDATORS.get(str_clean[:1])
    if len(str_clean) != _LEN_CNS or fn_rule is None:
        return False
    return fn_rule(str_clean)
