"""The uniform interface every registered document offers."""

from __future__ import annotations

from collections.abc import Callable
from typing import NamedTuple


class DocumentStrategy(NamedTuple):
    """The three operations every registered document offers.

    Attributes
    ----------
    is_valid : Callable[[str], bool]
        Validates a document value.
    mask : Callable[[str], str]
        Formats a value; for a document with no official mask it returns the unmasked digits.
    unmask : Callable[[str], str]
        Normalises a value to its bare form.
    """

    is_valid: Callable[[str], bool]
    mask: Callable[[str], str]
    unmask: Callable[[str], str]
