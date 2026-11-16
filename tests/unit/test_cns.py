"""Unit tests for the CNS helpers."""

import pytest

from pure_docs_br import is_valid_cns, mask_cns, unmask_cns


LIST_VALID: list[str] = [
    "100000000010002",
    "173456789010007",
    "100000000060018",
    "700000000000005",
    "987654321012349",
]


@pytest.mark.parametrize("str_value", LIST_VALID)
def test_is_valid_cns_valid_returns_true(str_value: str) -> None:
    """The issue's valid examples pass."""
    assert is_valid_cns(str_value) is True


@pytest.mark.parametrize("str_value", LIST_VALID)
def test_is_valid_cns_masked_returns_true(str_value: str) -> None:
    """The issue's valid examples pass in masked form."""
    assert is_valid_cns(mask_cns(str_value)) is True


@pytest.mark.parametrize(
    "str_value",
    ["100000000010003", "700000000000006", "300000000000000", "10000000001000", "ABC"],
)
def test_is_valid_cns_invalid_returns_false(str_value: str) -> None:
    """The issue's invalid examples return False without raising."""
    assert is_valid_cns(str_value) is False


def test_is_valid_cns_dv_ten_branch_returns_true() -> None:
    """A definitive sum with remainder 1 takes the suffix 001 branch."""
    assert is_valid_cns("100000000060018") is True


def test_is_valid_cns_dv_ten_with_suffix_000_returns_false() -> None:
    """In the dv == 10 branch the suffix must be 001, not 000."""
    assert is_valid_cns("100000000060008") is False


@pytest.mark.parametrize("str_first", ["0", "3", "4", "5", "6"])
def test_is_valid_cns_invalid_first_digit_returns_false(str_first: str) -> None:
    """First digits 0, 3, 4, 5 and 6 are never valid."""
    assert is_valid_cns(str_first + "00000000010002") is False


def test_is_valid_cns_empty_returns_false() -> None:
    """An empty string is not a CNS."""
    assert is_valid_cns("") is False


def test_is_valid_cns_unicode_digits_returns_false() -> None:
    """Arabic-Indic digits are stripped, so the length no longer closes."""
    assert is_valid_cns("١٠٠٠٠٠٠٠٠٠١٠٠٠٢") is False


def test_unmask_cns_strips_float_artifact() -> None:
    """A trailing .0 is dropped."""
    assert unmask_cns("100000000010002.0") == "100000000010002"


def test_unmask_cns_does_not_pad_zeros() -> None:
    """A short value stays short: no valid CNS starts with 0."""
    assert unmask_cns("123") == "123"


def test_unmask_cns_drops_non_ascii_digits() -> None:
    """Only ASCII 0-9 survive unmasking."""
    assert unmask_cns("١٢3") == "3"


def test_unmask_cns_no_digits_returns_empty() -> None:
    """No digits yields an empty string."""
    assert unmask_cns("ABC") == ""


def test_mask_cns_formats() -> None:
    """15 digits get the XXX XXXX XXXX XXXX mask."""
    assert mask_cns("100000000010002") == "100 0000 0001 0002"


def test_mask_cns_wrong_length_returns_unmasked() -> None:
    """A short value comes back without mask."""
    assert mask_cns("123") == "123"


def test_cns_non_str_raises_type_error() -> None:
    """A non-str violates the type-checked contract."""
    with pytest.raises(TypeError):
        is_valid_cns(100000000010002)  # type: ignore[arg-type]
