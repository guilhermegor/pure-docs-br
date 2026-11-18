"""Unit tests for the CNH helpers."""

import pytest

from pure_docs_br import is_valid_cnh, mask_cnh, unmask_cnh


LIST_VALID: list[str] = [
    "12345678900",
    "98765432109",
    "00000000119",
    "11111111220",
    "24681357982",
    "10000000091",
]


@pytest.mark.parametrize("str_value", LIST_VALID)
def test_is_valid_cnh_valid_returns_true(str_value: str) -> None:
    """The issue's valid examples pass."""
    assert is_valid_cnh(str_value) is True


@pytest.mark.parametrize("str_value", LIST_VALID)
def test_is_valid_cnh_spaced_returns_true(str_value: str) -> None:
    """The issue's valid examples pass with spaces and punctuation."""
    assert is_valid_cnh(f" {str_value[:3]}.{str_value[3:]} ") is True


@pytest.mark.parametrize(
    "str_value",
    ["12345678901", "12345678910", "00000000000", "99999999999", "1234567890", "", "ABCDEFGHIJK"],
)
def test_is_valid_cnh_invalid_returns_false(str_value: str) -> None:
    """The issue's invalid examples return False without raising."""
    assert is_valid_cnh(str_value) is False


def test_is_valid_cnh_discount_branch_returns_true() -> None:
    """A dv1 remainder of 10 becomes 0, discounts dv2 by 2 and lifts a negative by 11."""
    assert is_valid_cnh("98765432109") is True


def test_is_valid_cnh_non_str_raises_type_error() -> None:
    """A non-str argument is rejected by the runtime type checker."""
    with pytest.raises(TypeError):
        is_valid_cnh(12345678900)  # type: ignore[arg-type]


def test_unmask_cnh_float_tail_stripped() -> None:
    """The float ``.0`` tail is dropped."""
    assert unmask_cnh("12345678900.0") == "12345678900"


def test_unmask_cnh_short_digits_zero_padded() -> None:
    """Digits-only input is left-padded with zeros to 11."""
    assert unmask_cnh("119") == "00000000119"


def test_unmask_cnh_no_digits_returns_empty() -> None:
    """Input with no digits yields an empty string."""
    assert unmask_cnh("ABC") == ""


def test_mask_cnh_applies_pattern() -> None:
    """Each N takes the next digit and other characters are copied."""
    assert mask_cnh("02650306461", str_pattern="NNN NNNN NNNN") == "026 5030 6461"


def test_mask_cnh_unmasks_input_first() -> None:
    """A punctuated input is unmasked before the pattern is applied."""
    assert mask_cnh("026.50306461", str_pattern="NNN NNNN NNNN") == "026 5030 6461"


def test_mask_cnh_keeps_any_separator() -> None:
    """Characters other than N are copied as is."""
    assert mask_cnh("02650306461", str_pattern="N" * 11 + "/") == "02650306461/"


@pytest.mark.parametrize("str_pattern", ["", "NNN", "N" * 10, "N" * 12])
def test_mask_cnh_wrong_slot_count_raises(str_pattern: str) -> None:
    """A pattern without exactly 11 N raises ValueError."""
    with pytest.raises(ValueError, match="exactly 11"):
        mask_cnh("02650306461", str_pattern=str_pattern)


@pytest.mark.parametrize("str_value", ["", "ABC", "123456789012"])
def test_mask_cnh_unmaskable_input_returns_bare_value(str_value: str) -> None:
    """Empty, digitless or over-long input never raises and comes back unmasked."""
    assert mask_cnh(str_value, str_pattern="NNN NNNN NNNN") == unmask_cnh(str_value)


def test_mask_cnh_non_str_raises_type_error() -> None:
    """A non-str argument is rejected by the runtime type checker."""
    with pytest.raises(TypeError):
        mask_cnh(1, str_pattern="NNN NNNN NNNN")  # type: ignore[arg-type]
