"""Unit tests for the private mask-pattern helper."""

import pytest

from purepii_br._internal.utils.mask_pattern import apply_mask_pattern


def test_apply_mask_pattern_fills_slots_in_order() -> None:
    """Each N takes the next digit and other characters are copied."""
    assert apply_mask_pattern("123456", str_pattern="NN.NN-NN", int_len=6) == "12.34-56"


def test_apply_mask_pattern_wrong_slot_count_raises() -> None:
    """A pattern without exactly int_len N raises ValueError."""
    with pytest.raises(ValueError, match="exactly 6 'N', found 5"):
        apply_mask_pattern("123456", str_pattern="NNNNN", int_len=6)


def test_apply_mask_pattern_wrong_digit_count_returns_digits() -> None:
    """Digits that are not int_len long come back unchanged."""
    assert apply_mask_pattern("123", str_pattern="NN-NN", int_len=4) == "123"


def test_apply_mask_pattern_non_str_raises_type_error() -> None:
    """A non-str argument is rejected by the runtime type checker."""
    with pytest.raises(TypeError):
        apply_mask_pattern(123, str_pattern="NNN", int_len=3)  # type: ignore[arg-type]
