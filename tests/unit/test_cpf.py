"""Unit tests for the CPF helpers."""

from decimal import Decimal

import pytest

from purepii_br import is_valid_cpf, mask_cpf, unmask_cpf


def test_unmask_cpf_masked_value_returns_bare_digits() -> None:
    """A punctuated CPF unmasks to its 11 bare digits."""
    assert unmask_cpf("529.982.247-25") == "52998224725"


def test_unmask_cpf_float_artifact_drops_trailing_zero_decimal() -> None:
    """A float→str ``.0`` tail is stripped from a CPF."""
    assert unmask_cpf("52998224725.0") == "52998224725"


def test_unmask_cpf_short_numeric_left_zero_pads_to_11() -> None:
    """A short CPF is left-zero-padded to 11."""
    assert unmask_cpf("1234567") == "00001234567"


def test_mask_cpf_bare_value_returns_punctuated() -> None:
    """A bare CPF is formatted as ``XXX.XXX.XXX-XX``."""
    assert mask_cpf("52998224725") == "529.982.247-25"


def test_is_valid_cpf_valid_value_true() -> None:
    """A correct CPF validates."""
    assert is_valid_cpf("529.982.247-25") is True


def test_is_valid_cpf_wrong_check_digit_false() -> None:
    """A CPF with a wrong check digit is rejected."""
    assert is_valid_cpf("52998224726") is False


def test_is_valid_cpf_repeated_digits_false() -> None:
    """A repeated-digit CPF is rejected."""
    assert is_valid_cpf("11111111111") is False


def test_is_valid_cpf_short_input_is_zero_padded_true() -> None:
    """``"191"`` pads to ``00000000191``, a CPF with correct check digits (pinned behaviour)."""
    assert is_valid_cpf("191") is True


def test_is_valid_cpf_single_zero_padded_repeated_digits_false() -> None:
    """``"0"`` pads to ``00000000000``, which is rejected as repeated digits."""
    assert is_valid_cpf("0") is False


@pytest.mark.parametrize("fn_call", [is_valid_cpf, mask_cpf])
@pytest.mark.parametrize("obj_value", [None, Decimal("1.5"), 52998224725])
def test_functions_non_str_raise_type_error(*, fn_call: object, obj_value: object) -> None:
    """Every CPF function rejects a non-``str`` with ``TypeError``."""
    with pytest.raises(TypeError):
        fn_call(obj_value)  # type: ignore[operator]


@pytest.mark.parametrize(
    ("fn_call", "str_value"),
    [
        (mask_cpf, ""),
        (mask_cpf, "123456789012"),
    ],
)
def test_mask_not_document_length_returns_unmasked_value(
    *, fn_call: object, str_value: str
) -> None:
    """``mask_cpf`` returns the unmasked value when it is empty or too long."""
    assert fn_call(str_value) == str_value  # type: ignore[operator]


@pytest.mark.parametrize("fn_call", [is_valid_cpf])
def test_is_valid_empty_str_false(fn_call: object) -> None:
    """An empty string is invalid, not an error."""
    assert fn_call("") is False  # type: ignore[operator]


LIST_NON_ASCII_CPF: list[str] = ["٥٢٩٩٨٢٢٤٧٢٥", "５２９９８２２４７２５"]


@pytest.mark.parametrize("str_value", LIST_NON_ASCII_CPF)
def test_unmask_cpf_non_ascii_digits_returns_empty(str_value: str) -> None:
    """Arabic-Indic and full-width digits are dropped, never kept."""
    assert unmask_cpf(str_value) == ""


@pytest.mark.parametrize("str_value", LIST_NON_ASCII_CPF)
def test_is_valid_cpf_non_ascii_digits_returns_false(str_value: str) -> None:
    """Arabic-Indic and full-width digits are not a valid CPF."""
    assert is_valid_cpf(str_value) is False
