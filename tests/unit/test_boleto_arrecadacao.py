"""Unit tests for the utility-bill slip (boleto de arrecadacao) helpers."""

import pytest

from pure_docs_br import (
    is_valid_boleto_arrecadacao,
    mask_boleto_arrecadacao,
    unmask_boleto_arrecadacao,
)


_BAR_1 = "81680000001234500000000000000000000000000000"
_BAR_2 = "82680000005432112345678901234567890123456789"
_BAR_3 = "83800000009999998765432109876543210987654321"
_LINE_1 = "816800000019234500000000000000000000000000000000"
_LINE_2 = "826800000059432112345678890123456786901234567898"
_LINE_3 = "838000000092999998765437210987654322109876543212"
_LINE_1_MASKED = "81680000001-9 23450000000-0 00000000000-0 00000000000-0"
_LINE_3_MASKED = "83800000009-2 99999876543-7 21098765432-2 10987654321-2"
_BAR_REM_ZERO = "83806956042304114426942080939729806351396937"
_BAR_REM_ONE = "83802791198962246390765682808141412917366625"
_BAR_REM_TEN = "83816115971439875428343351417195364052594351"
_FULL_WIDTH = "０" * 5
_ARABIC_INDIC = "٠" * 5


def _swap_char(str_value: str, *, int_idx: int, str_char: str) -> str:
    """Return ``str_value`` with the character at ``int_idx`` replaced."""
    return str_value[:int_idx] + str_char + str_value[int_idx + 1 :]


@pytest.mark.parametrize("str_value", [_BAR_1, _BAR_2, _BAR_3, _LINE_1, _LINE_2, _LINE_3])
def test_is_valid_boleto_arrecadacao_issue_valid_examples_return_true(str_value: str) -> None:
    """The issue's barcodes and typeable lines pass."""
    assert is_valid_boleto_arrecadacao(str_value) is True


@pytest.mark.parametrize("str_value", [_LINE_1_MASKED, _LINE_3_MASKED])
def test_is_valid_boleto_arrecadacao_masked_line_returns_true(str_value: str) -> None:
    """The hyphenated, spaced line passes."""
    assert is_valid_boleto_arrecadacao(str_value) is True


@pytest.mark.parametrize(
    "str_value",
    [
        "81690000001234500000000000000000000000000000",
        "71680000001234500000000000000000000000000000",
        "8168000000123450000000000000000000000000000",
        "",
    ],
)
def test_is_valid_boleto_arrecadacao_issue_invalid_examples_return_false(str_value: str) -> None:
    """The issue's invalid examples return False without raising."""
    assert is_valid_boleto_arrecadacao(str_value) is False


@pytest.mark.parametrize("int_idx", [11, 23, 35, 47])
def test_is_valid_boleto_arrecadacao_wrong_block_dv_returns_false(int_idx: int) -> None:
    """A wrong DV in any of the four blocks fails the line."""
    str_dv = str((int(_LINE_1[int_idx]) + 1) % 10)
    str_line = _swap_char(_LINE_1, int_idx=int_idx, str_char=str_dv)
    assert is_valid_boleto_arrecadacao(str_line) is False


def test_is_valid_boleto_arrecadacao_line_with_wrong_general_dv_returns_false() -> None:
    """Block DVs alone do not make a line valid: the rebuilt barcode must pass too."""
    str_line = "816900000019234500000000000000000000000000000000"
    assert is_valid_boleto_arrecadacao(str_line) is False


@pytest.mark.parametrize("str_digit", ["0", "1", "2", "3", "4", "5"])
def test_is_valid_boleto_arrecadacao_value_id_outside_six_to_nine_returns_false(
    str_digit: str,
) -> None:
    """A 3rd digit outside 6-9 picks no module and is invalid."""
    assert is_valid_boleto_arrecadacao(_swap_char(_BAR_1, int_idx=2, str_char=str_digit)) is False


def test_is_valid_boleto_arrecadacao_line_value_id_outside_six_to_nine_returns_false() -> None:
    """A line whose 3rd digit is outside 6-9 is invalid."""
    assert is_valid_boleto_arrecadacao(_swap_char(_LINE_1, int_idx=2, str_char="5")) is False


@pytest.mark.parametrize("str_value", [_BAR_REM_ZERO, _BAR_REM_ONE])
def test_is_valid_boleto_arrecadacao_mod11_remainder_zero_or_one_gives_dv_zero(
    str_value: str,
) -> None:
    """A mod 11 remainder of 0 or 1 gives DV 0."""
    assert is_valid_boleto_arrecadacao(str_value) is True


@pytest.mark.parametrize("str_value", [_BAR_REM_ZERO, _BAR_REM_ONE])
def test_is_valid_boleto_arrecadacao_mod11_remainder_zero_or_one_rejects_dv_one(
    str_value: str,
) -> None:
    """The cobranca fallback (DV 1) is not accepted for remainder 0 or 1."""
    assert is_valid_boleto_arrecadacao(_swap_char(str_value, int_idx=3, str_char="1")) is False


def test_is_valid_boleto_arrecadacao_mod11_remainder_ten_gives_dv_one() -> None:
    """A mod 11 remainder of 10 gives DV 1."""
    assert is_valid_boleto_arrecadacao(_BAR_REM_TEN) is True


def test_is_valid_boleto_arrecadacao_mod11_remainder_ten_rejects_dv_zero() -> None:
    """Remainder 10 is not DV 0."""
    assert is_valid_boleto_arrecadacao(_swap_char(_BAR_REM_TEN, int_idx=3, str_char="0")) is False


def test_is_valid_boleto_arrecadacao_float_tail_returns_true() -> None:
    """A float-coerced barcode is accepted."""
    assert is_valid_boleto_arrecadacao(_BAR_1 + ".0") is True


@pytest.mark.parametrize("str_value", ["８" + _BAR_1[1:], "٨" + _BAR_1[1:]])
def test_is_valid_boleto_arrecadacao_non_ascii_digits_return_false(str_value: str) -> None:
    """Full-width and Arabic-Indic digits are never accepted."""
    assert is_valid_boleto_arrecadacao(str_value) is False


def test_is_valid_boleto_arrecadacao_non_str_raises_type_error() -> None:
    """A non-str argument is rejected by the runtime type checker."""
    with pytest.raises(TypeError):
        is_valid_boleto_arrecadacao(123)  # type: ignore[arg-type]


def test_unmask_boleto_arrecadacao_masked_input_returns_digits() -> None:
    """A masked line unmasks to its 48 digits."""
    assert unmask_boleto_arrecadacao(_LINE_1_MASKED) == _LINE_1


def test_unmask_boleto_arrecadacao_float_tail_is_dropped() -> None:
    """A float ``.0`` tail is removed from an all-digit value."""
    assert unmask_boleto_arrecadacao(_BAR_1 + ".0") == _BAR_1


def test_unmask_boleto_arrecadacao_does_not_pad() -> None:
    """Short input is not padded."""
    assert unmask_boleto_arrecadacao("123") == "123"


def test_unmask_boleto_arrecadacao_empty_returns_empty() -> None:
    """Empty stays empty."""
    assert unmask_boleto_arrecadacao("") == ""


@pytest.mark.parametrize("str_value", [_FULL_WIDTH, _ARABIC_INDIC])
def test_unmask_boleto_arrecadacao_non_ascii_digits_are_dropped(str_value: str) -> None:
    """Full-width and Arabic-Indic digits are filtered out."""
    assert unmask_boleto_arrecadacao(str_value) == ""


def test_mask_boleto_arrecadacao_forty_eight_digits_returns_masked_line() -> None:
    """A 48-digit line gets four hyphenated blocks."""
    assert mask_boleto_arrecadacao(_LINE_3) == _LINE_3_MASKED


def test_mask_boleto_arrecadacao_masked_input_is_stable() -> None:
    """Masking an already masked line is a no-op."""
    assert mask_boleto_arrecadacao(_LINE_3_MASKED) == _LINE_3_MASKED


def test_mask_boleto_arrecadacao_forty_four_digits_returns_unmasked() -> None:
    """A 44-digit barcode has no mask."""
    assert mask_boleto_arrecadacao(_BAR_1) == _BAR_1


def test_mask_boleto_arrecadacao_wrong_length_returns_unmasked() -> None:
    """A length that closes neither shape comes back bare."""
    assert mask_boleto_arrecadacao("12.345") == "12345"


@pytest.mark.parametrize("str_value", [_FULL_WIDTH, _ARABIC_INDIC])
def test_mask_boleto_arrecadacao_non_ascii_digits_never_pass_through(str_value: str) -> None:
    """Non-ASCII digits never reach the output."""
    assert mask_boleto_arrecadacao(str_value) == ""
