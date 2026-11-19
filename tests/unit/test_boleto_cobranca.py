"""Unit tests for the bank collection slip (boleto de cobranca) helpers."""

import pytest

from purepii_br import (
    is_valid_boleto_cobranca,
    mask_boleto_cobranca,
    unmask_boleto_cobranca,
)


_BAR_1 = "00191999900000123450000000000000000000000001"
_BAR_2 = "23792800000001000001234512345123451234512345"
_BAR_3 = "34196000000000000009876598765987659876598765"
_LINE_1 = "00190000090000000000000000000018199990000012345"
_LINE_2 = "23791234541234512345412345123454280000000100000"
_LINE_3 = "34199876509876598765098765987650600000000000000"
_LINE_1_MASKED = "00190.00009 00000.000000 00000.000018 1 99990000012345"
_LINE_2_MASKED = "23791.23454 12345.123454 12345.123454 2 80000000100000"
_BAR_REM_ZERO = "00191999900000123450000000000000000000000007"
_BAR_REM_ONE = "00191999900000123450000000000000000000000002"
_FULL_WIDTH = "０" * 5
_ARABIC_INDIC = "٠" * 5


@pytest.mark.parametrize("str_value", [_BAR_1, _BAR_2, _BAR_3, _LINE_1, _LINE_2, _LINE_3])
def test_is_valid_boleto_cobranca_issue_valid_examples_return_true(str_value: str) -> None:
    """The issue's barcodes and typeable lines pass."""
    assert is_valid_boleto_cobranca(str_value) is True


@pytest.mark.parametrize("str_value", [_LINE_1_MASKED, _LINE_2_MASKED])
def test_is_valid_boleto_cobranca_masked_line_returns_true(str_value: str) -> None:
    """The printed, punctuated line passes."""
    assert is_valid_boleto_cobranca(str_value) is True


@pytest.mark.parametrize(
    "str_value",
    [
        "00192999900000123450000000000000000000000001",
        "00190000090000000000000000000018199990000012346",
        "0019100000000000000000000000000000000000000",
        "",
    ],
)
def test_is_valid_boleto_cobranca_issue_invalid_examples_return_false(str_value: str) -> None:
    """The issue's invalid examples return False without raising."""
    assert is_valid_boleto_cobranca(str_value) is False


@pytest.mark.parametrize("int_idx", [9, 20, 31])
def test_is_valid_boleto_cobranca_wrong_field_dv_returns_false(int_idx: int) -> None:
    """A wrong mod 10 digit in field 1, 2 or 3 fails."""
    str_dv = str((int(_LINE_1[int_idx]) + 1) % 10)
    assert is_valid_boleto_cobranca(_LINE_1[:int_idx] + str_dv + _LINE_1[int_idx + 1 :]) is False


@pytest.mark.parametrize("str_value", [_BAR_REM_ZERO, _BAR_REM_ONE])
def test_is_valid_boleto_cobranca_remainder_zero_or_one_gives_dv_one(str_value: str) -> None:
    """A mod 11 result of 11 or 10 (remainder 0 or 1) becomes DV 1."""
    assert is_valid_boleto_cobranca(str_value) is True


@pytest.mark.parametrize("str_value", [_BAR_REM_ZERO, _BAR_REM_ONE])
def test_is_valid_boleto_cobranca_remainder_zero_or_one_rejects_other_dv(
    str_value: str,
) -> None:
    """For those remainders neither 0 nor 10 nor 11 is an accepted digit."""
    assert is_valid_boleto_cobranca(str_value[:4] + "0" + str_value[5:]) is False


def test_is_valid_boleto_cobranca_float_tail_returns_true() -> None:
    """A float-coerced barcode is accepted."""
    assert is_valid_boleto_cobranca(_BAR_1 + ".0") is True


@pytest.mark.parametrize("str_value", ["００" + _BAR_1[2:], "٠٠" + _BAR_1[2:]])
def test_is_valid_boleto_cobranca_non_ascii_digits_return_false(str_value: str) -> None:
    """Full-width and Arabic-Indic digits are never accepted."""
    assert is_valid_boleto_cobranca(str_value) is False


def test_is_valid_boleto_cobranca_non_str_raises_type_error() -> None:
    """A non-str argument is rejected by the runtime type checker."""
    with pytest.raises(TypeError):
        is_valid_boleto_cobranca(123)  # type: ignore[arg-type]


def test_unmask_boleto_cobranca_issue_masked_input_returns_digits() -> None:
    """The issue's masked line unmasks to its 47 digits."""
    assert unmask_boleto_cobranca(_LINE_1_MASKED) == _LINE_1


def test_unmask_boleto_cobranca_float_tail_is_dropped() -> None:
    """A float ``.0`` tail is removed."""
    assert unmask_boleto_cobranca(_BAR_1 + ".0") == _BAR_1


def test_unmask_boleto_cobranca_does_not_pad() -> None:
    """Short input is not padded."""
    assert unmask_boleto_cobranca("123") == "123"


def test_unmask_boleto_cobranca_empty_returns_empty() -> None:
    """Empty stays empty."""
    assert unmask_boleto_cobranca("") == ""


@pytest.mark.parametrize("str_value", [_FULL_WIDTH, _ARABIC_INDIC])
def test_unmask_boleto_cobranca_non_ascii_digits_are_dropped(str_value: str) -> None:
    """Full-width and Arabic-Indic digits are filtered out."""
    assert unmask_boleto_cobranca(str_value) == ""


def test_mask_boleto_cobranca_forty_seven_digits_returns_masked_line() -> None:
    """A 47-digit line gets the printed mask."""
    assert mask_boleto_cobranca(_LINE_1) == _LINE_1_MASKED


def test_mask_boleto_cobranca_masked_input_is_stable() -> None:
    """Masking an already masked line is a no-op."""
    assert mask_boleto_cobranca(_LINE_1_MASKED) == _LINE_1_MASKED


def test_mask_boleto_cobranca_forty_four_digits_returns_unmasked() -> None:
    """A 44-digit barcode has no mask."""
    assert mask_boleto_cobranca(_BAR_1) == _BAR_1


def test_mask_boleto_cobranca_wrong_length_returns_unmasked() -> None:
    """A length that closes neither shape comes back bare."""
    assert mask_boleto_cobranca("12.345") == "12345"


@pytest.mark.parametrize("str_value", [_FULL_WIDTH, _ARABIC_INDIC])
def test_mask_boleto_cobranca_non_ascii_digits_never_pass_through(str_value: str) -> None:
    """Non-ASCII digits never reach the output."""
    assert mask_boleto_cobranca(str_value) == ""
