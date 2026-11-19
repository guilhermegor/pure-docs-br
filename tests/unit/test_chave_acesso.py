"""Unit tests for the fiscal document access key helpers."""

import pytest

from purepii_br import is_valid_chave_acesso, mask_chave_acesso, unmask_chave_acesso


_NFE = "35231111222333000181550010000000011123456789"
_CTE = "41240811444777000161570010000012341876543218"
_NFCE = "33250111222333000181650020000009871000000018"
_ALPHA = "35231112ABC34501DE35550010000000011123456780"
_REM_ZERO = "35231111222333000181550010000000000412345670"
_REM_ONE = "35231111222333000181550010000000100012345670"
_NFE_MASKED = "3523 1111 2223 3300 0181 5500 1000 0000 0111 2345 6789"


@pytest.mark.parametrize("str_value", [_NFE, _CTE, _NFCE])
def test_is_valid_chave_acesso_issue_valid_examples_return_true(str_value: str) -> None:
    """The issue's valid examples pass."""
    assert is_valid_chave_acesso(str_value) is True


@pytest.mark.parametrize("str_value", [_NFE, _CTE, _NFCE])
def test_is_valid_chave_acesso_spaced_returns_true(str_value: str) -> None:
    """The DANFE spaced form passes."""
    assert is_valid_chave_acesso(mask_chave_acesso(str_value)) is True


@pytest.mark.parametrize("str_value", [_NFE, _CTE, _NFCE])
def test_is_valid_chave_acesso_nfe_prefix_returns_true(str_value: str) -> None:
    """The XML ``Id`` prefix is dropped before checking."""
    assert is_valid_chave_acesso("NFe" + str_value) is True


@pytest.mark.parametrize(
    "str_value",
    [
        "35231111222333000181550010000000011123456780",
        "3523111122233300018155001000000001112345678",
        "",
    ],
)
def test_is_valid_chave_acesso_issue_invalid_examples_return_false(str_value: str) -> None:
    """The issue's invalid examples return False without raising."""
    assert is_valid_chave_acesso(str_value) is False


@pytest.mark.parametrize("str_value", [_REM_ZERO, _REM_ONE])
def test_is_valid_chave_acesso_remainder_zero_or_one_gives_dv_zero(str_value: str) -> None:
    """A remainder of 0 or 1 makes the check digit 0."""
    assert is_valid_chave_acesso(str_value) is True


@pytest.mark.parametrize("str_value", [_REM_ZERO, _REM_ONE])
def test_is_valid_chave_acesso_remainder_zero_or_one_rejects_other_dv(str_value: str) -> None:
    """For those remainders any other check digit is wrong (11 - r is not used)."""
    assert is_valid_chave_acesso(str_value[:-1] + "1") is False


def test_is_valid_chave_acesso_alphanumeric_cnpj_returns_true() -> None:
    """Letters in the CNPJ part count as ``ord - 48`` (NT 2025.001)."""
    assert is_valid_chave_acesso(_ALPHA) is True


def test_is_valid_chave_acesso_alphanumeric_lowercase_returns_true() -> None:
    """Lowercase letters are uppercased by unmask."""
    assert is_valid_chave_acesso(_ALPHA.lower()) is True


def test_is_valid_chave_acesso_alphanumeric_wrong_dv_returns_false() -> None:
    """A changed check digit on an alphanumeric key fails."""
    assert is_valid_chave_acesso(_ALPHA[:-1] + "1") is False


def test_is_valid_chave_acesso_letter_outside_cnpj_returns_false() -> None:
    """Letters are only allowed in positions 7 to 18."""
    assert is_valid_chave_acesso("A" + _NFE[1:]) is False


def test_is_valid_chave_acesso_letter_in_cnpj_check_digits_returns_false() -> None:
    """The last two CNPJ characters stay numeric."""
    assert is_valid_chave_acesso(_NFE[:18] + "AB" + _NFE[20:]) is False


@pytest.mark.parametrize("str_value", ["３５" + _NFE[2:], "٣٥" + _NFE[2:]])
def test_is_valid_chave_acesso_non_ascii_digits_return_false(str_value: str) -> None:
    """Full-width and Arabic-Indic digits are never accepted."""
    assert is_valid_chave_acesso(str_value) is False


def test_is_valid_chave_acesso_float_tail_returns_true() -> None:
    """A float-coerced key is accepted."""
    assert is_valid_chave_acesso(_NFE + ".0") is True


def test_is_valid_chave_acesso_non_str_raises_type_error() -> None:
    """A non-str argument raises TypeError from the type checker."""
    with pytest.raises(TypeError):
        is_valid_chave_acesso(123)  # type: ignore[arg-type]


def test_unmask_chave_acesso_drops_nfe_prefix() -> None:
    """The ``NFe`` prefix of the XML ``Id`` attribute is removed."""
    assert unmask_chave_acesso("NFe" + _NFE) == _NFE


@pytest.mark.parametrize("str_prefix", ["CTe", "MDFe", "nfe"])
def test_unmask_chave_acesso_drops_other_prefixes(str_prefix: str) -> None:
    """``CTe``, ``MDFe`` and lowercase prefixes are removed too."""
    assert unmask_chave_acesso(str_prefix + _NFE) == _NFE


def test_unmask_chave_acesso_strips_spaces() -> None:
    """Spaces are removed."""
    assert unmask_chave_acesso(_NFE_MASKED) == _NFE


def test_unmask_chave_acesso_float_tail_is_dropped() -> None:
    """A float ``.0`` tail is removed."""
    assert unmask_chave_acesso(_NFE + ".0") == _NFE


def test_unmask_chave_acesso_keeps_and_uppercases_letters() -> None:
    """Letters survive and are uppercased."""
    assert unmask_chave_acesso(_ALPHA.lower()) == _ALPHA


def test_unmask_chave_acesso_does_not_pad() -> None:
    """Short keys are not zero-padded."""
    assert unmask_chave_acesso("123") == "123"


def test_unmask_chave_acesso_empty_returns_empty() -> None:
    """Empty input stays empty."""
    assert unmask_chave_acesso("") == ""


@pytest.mark.parametrize("str_value", ["３５１", "٣٥١"])
def test_unmask_chave_acesso_non_ascii_digits_are_dropped(str_value: str) -> None:
    """Full-width and Arabic-Indic digits are filtered out."""
    assert unmask_chave_acesso(str_value) == ""


@pytest.mark.parametrize("str_value", ["ß", "ſ", "ı"])
def test_unmask_chave_acesso_non_ascii_letters_never_become_ascii(str_value: str) -> None:
    """Letters whose ``upper()`` is ASCII are filtered before uppercasing."""
    assert unmask_chave_acesso(str_value) == ""


def test_mask_chave_acesso_forty_four_returns_eleven_groups() -> None:
    """A 44-character key gets 11 groups of 4."""
    assert mask_chave_acesso(_NFE) == _NFE_MASKED


def test_mask_chave_acesso_masked_input_is_stable() -> None:
    """Masking an already masked key is a no-op."""
    assert mask_chave_acesso(_NFE_MASKED) == _NFE_MASKED


def test_mask_chave_acesso_alphanumeric_keeps_letters() -> None:
    """Letters appear uppercased inside the groups."""
    assert mask_chave_acesso(_ALPHA.lower()).startswith("3523 1112 ABC3 4501 DE35")


def test_mask_chave_acesso_forty_three_returns_unmasked() -> None:
    """A 43-digit value cannot be masked: the bare value comes back."""
    assert mask_chave_acesso(_NFE[:-1]) == _NFE[:-1]


def test_mask_chave_acesso_full_width_digits_never_pass_through() -> None:
    """Full-width digits are dropped, leaving nothing to mask."""
    assert mask_chave_acesso("１２３") == ""


def test_unmask_chave_acesso_prefix_letters_inside_key_are_kept() -> None:
    """Only a leading prefix is dropped; ``NFE`` inside a CNPJ stays."""
    assert unmask_chave_acesso("35231112NFE345NFE3555") == "35231112NFE345NFE3555"
