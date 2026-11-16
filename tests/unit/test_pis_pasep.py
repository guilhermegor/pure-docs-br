"""Unit tests for the PIS/PASEP/NIT/NIS helpers."""

import pytest

from pure_docs_br import is_valid_pis_pasep, mask_pis_pasep, unmask_pis_pasep


LIST_VALID: list[str] = ["12345678900", "20000000013", "12034567899", "11111111124"]


@pytest.mark.parametrize("str_value", LIST_VALID)
def test_is_valid_pis_pasep_valid_returns_true(str_value: str) -> None:
    """The issue's valid examples pass."""
    assert is_valid_pis_pasep(str_value) is True


@pytest.mark.parametrize("str_value", LIST_VALID)
def test_is_valid_pis_pasep_masked_returns_true(str_value: str) -> None:
    """The issue's valid examples pass in masked form."""
    assert is_valid_pis_pasep(mask_pis_pasep(str_value)) is True


@pytest.mark.parametrize(
    "str_value",
    ["12345678901", "20000000014", "11111111111", "00000000000", "123456789001", "ABC", ""],
)
def test_is_valid_pis_pasep_invalid_returns_false(str_value: str) -> None:
    """The issue's invalid examples return False without raising."""
    assert is_valid_pis_pasep(str_value) is False


def test_is_valid_pis_pasep_dv_ten_becomes_zero() -> None:
    """A weighted sum with remainder 1 gives 10, which folds to 0."""
    assert is_valid_pis_pasep("40000000000") is True


def test_is_valid_pis_pasep_dv_ten_nonzero_returns_false() -> None:
    """After the fold, only 0 is the right check digit."""
    assert is_valid_pis_pasep("40000000001") is False


def test_unmask_pis_pasep_strips_float_artifact() -> None:
    """A trailing .0 is dropped."""
    assert unmask_pis_pasep("12345678900.0") == "12345678900"


def test_unmask_pis_pasep_pads_zeros() -> None:
    """A zero-stripped value is restored to 11 digits."""
    assert unmask_pis_pasep("1234567890") == "01234567890"


def test_unmask_pis_pasep_empty_returns_empty() -> None:
    """No digits yields an empty string."""
    assert unmask_pis_pasep("ABC") == ""


def test_mask_pis_pasep_formats() -> None:
    """11 digits get the XXX.XXXXX.XX-X mask."""
    assert mask_pis_pasep("12345678900") == "123.45678.90-0"


def test_mask_pis_pasep_wrong_length_returns_unmasked() -> None:
    """A 12-digit value comes back without mask."""
    assert mask_pis_pasep("123456789001") == "123456789001"


def test_pis_pasep_non_str_raises_type_error() -> None:
    """A non-str violates the type-checked contract."""
    with pytest.raises(TypeError):
        is_valid_pis_pasep(12345678900)  # type: ignore[arg-type]
