"""Unit tests for the RG and CIN helpers."""

import pytest

from pure_docs_br import is_valid_cin, is_valid_rg, unmask_rg
from pure_docs_br.rg import _DICT_VALIDATORS, _compute_rj_dv, _compute_sp_dv


LIST_SP_VALID: list[str] = [
    "120300011",
    "123456782",
    "246801359",
    "000000012",
    "10000006X",
    "10000023X",
    "12.030.001-1",
    "10.000.006-x",
    "12345678",
]
LIST_SP_INVALID: list[str] = [
    "123456783",
    "12345678X",
    "1234567890",
    "",
    "ABCDEFGHI",
]
LIST_RJ_VALID: list[str] = ["123456782", "12.345.678-2", "111111118", "000000018"]
LIST_RJ_INVALID: list[str] = ["123456783", "12345678", "12345678X", ""]
LIST_UF_UNSOURCED: list[str] = ["AC", "BA", "RS", "PR", "TO", "DF"]
LIST_GENERIC_VALID: list[str] = ["1234567", "123456789", "1234567890", "12345678X", "0123456"]
LIST_GENERIC_INVALID: list[str] = ["123456", "12345678901", "X2345678", "AB1234567", ""]


@pytest.mark.parametrize("str_value", LIST_SP_VALID)
def test_is_valid_rg_sp_valid_returns_true(str_value: str) -> None:
    """SP values with a correct DV, or 8 format-only digits, pass."""
    assert is_valid_rg(str_value, str_uf="SP") is True


@pytest.mark.parametrize("str_value", LIST_SP_INVALID)
def test_is_valid_rg_sp_invalid_returns_false(str_value: str) -> None:
    """SP values with a wrong DV, wrong length or letters fail without raising."""
    assert is_valid_rg(str_value, str_uf="SP") is False


@pytest.mark.parametrize("str_value", LIST_RJ_VALID)
def test_is_valid_rg_rj_valid_returns_true(str_value: str) -> None:
    """RJ values with the modulo-10 DV pass."""
    assert is_valid_rg(str_value, str_uf="RJ") is True


@pytest.mark.parametrize("str_value", LIST_RJ_INVALID)
def test_is_valid_rg_rj_invalid_returns_false(str_value: str) -> None:
    """RJ values with a wrong DV or wrong shape fail."""
    assert is_valid_rg(str_value, str_uf="RJ") is False


def test_is_valid_rg_mg_eight_digits_returns_true() -> None:
    """MG is format-only: 8 digits pass."""
    assert is_valid_rg("12345678", str_uf="MG") is True


def test_is_valid_rg_mg_seven_digits_returns_true() -> None:
    """MG accepts a 7-digit RG (TCE-MG record M-6.691.335)."""
    assert is_valid_rg("6.691.335", str_uf="MG") is True


def test_is_valid_rg_mg_nine_digits_returns_false() -> None:
    """MG rejects a 9-character value."""
    assert is_valid_rg("123456789", str_uf="MG") is False


@pytest.mark.parametrize("str_uf", LIST_UF_UNSOURCED)
def test_is_valid_rg_unsourced_uf_raises_not_implemented(str_uf: str) -> None:
    """A UF without a sourced rule raises instead of answering."""
    with pytest.raises(NotImplementedError):
        is_valid_rg("123456789", str_uf=str_uf)


@pytest.mark.parametrize("str_uf", ["XX", "sp", "Sp", ""])
def test_is_valid_rg_unknown_uf_raises_value_error(str_uf: str) -> None:
    """An unknown or non-uppercase UF raises ValueError."""
    with pytest.raises(ValueError, match="unknown UF"):
        is_valid_rg("123456789", str_uf=str_uf)


def test_dict_validators_covers_all_27_ufs() -> None:
    """The router has an entry for each of the 27 UFs."""
    assert len(_DICT_VALIDATORS) == 27  # noqa: PLR2004


@pytest.mark.parametrize("str_value", LIST_GENERIC_VALID)
def test_is_valid_rg_no_uf_valid_returns_true(str_value: str) -> None:
    """Without a UF, 7 to 10 chars with X only last pass."""
    assert is_valid_rg(str_value) is True


@pytest.mark.parametrize("str_value", LIST_GENERIC_INVALID)
def test_is_valid_rg_no_uf_invalid_returns_false(str_value: str) -> None:
    """Without a UF, wrong length or misplaced letters fail."""
    assert is_valid_rg(str_value) is False


def test_unmask_rg_strips_punctuation() -> None:
    """Dots and dash are removed."""
    assert unmask_rg("12.030.001-1") == "120300011"


def test_unmask_rg_uppercases_x() -> None:
    """A lowercase X check digit is uppercased."""
    assert unmask_rg("10.000.006-x") == "10000006X"


def test_unmask_rg_strips_float_tail() -> None:
    """The float ``.0`` tail is dropped."""
    assert unmask_rg("123456789.0") == "123456789"


def test_unmask_rg_does_not_pad() -> None:
    """Leading zeros are not invented."""
    assert unmask_rg("123") == "123"


def test_is_valid_rg_non_str_raises_type_error() -> None:
    """A non-str raises from the runtime type checker."""
    with pytest.raises(TypeError):
        is_valid_rg(123456789)  # type: ignore[arg-type]


def test_compute_sp_dv_ten_becomes_x() -> None:
    """Remainder 10 is written X."""
    assert _compute_sp_dv("10000006") == "X"


def test_compute_rj_dv_matches_hand_calculation() -> None:
    """12345678 sums to 38 with nines out, so the DV is 2."""
    assert _compute_rj_dv("12345678") == 2  # noqa: PLR2004


def test_is_valid_cin_valid_cpf_returns_true() -> None:
    """A valid CPF is a valid CIN."""
    assert is_valid_cin("529.982.247-25") is True


def test_is_valid_cin_invalid_cpf_returns_false() -> None:
    """A wrong CPF check digit is an invalid CIN."""
    assert is_valid_cin("52998224726") is False
