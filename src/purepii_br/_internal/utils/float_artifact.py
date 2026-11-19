"""Float-coercion cleanup shared by every document module."""

from __future__ import annotations

import re

from purepii_br._internal.utils.typing import type_checker


_RE_FLOAT_ARTIFACT: re.Pattern[str] = re.compile(r"^\s*(\d+)\.0+\s*$")


@type_checker
def _strip_float_artifact(str_value: str) -> str:
    """Drop a trailing ``.0`` left by a float→str coercion; otherwise trim whitespace.

    Parameters
    ----------
    str_value : str
        Raw identifier as read from a source (CSV cell, DataFrame value, API field).

    Returns
    -------
    str
        ``str_value`` with a ``".0…"`` tail removed when it is an integer-with-float-tail,
        else the whitespace-trimmed input.
    """
    cls_match = _RE_FLOAT_ARTIFACT.match(str_value)
    if cls_match is not None:
        return cls_match.group(1)
    return str_value.strip()
