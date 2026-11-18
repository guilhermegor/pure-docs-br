"""Unit tests for the CAEPF helpers."""

import pytest

from pure_docs_br import is_valid_caepf, mask_caepf, unmask_caepf
from pure_docs_br.caepf import _compute_dvs


LIST_VALID: list[str] = [
    "00000002500171",
    "2500171",
    "11144477700154",
    "00000000100238",
    "98765432100315",
    "12345678900100",
]

LIST_INVALID: list[str] = [
    "11144477700155",
    "11144477700164",
    "11144477700073",
    "11111111100157",
    "1114447770015",
    "111444777001540",
    "",
    "ABCDEFGHIJKLMN",
]


@pytest.mark.parametrize("str_value", LIST_VALID)
def test_is_valid_caepf_valid_returns_true(str_value: str) -> None:
    """Accept the SERPRO sample and synthetic numbers, including the ``> 99`` branch."""
    assert is_valid_caepf(str_value) is True


@pytest.mark.parametrize("str_value", LIST_VALID)
def test_is_valid_caepf_masked_returns_true(str_value: str) -> None:
    """Accept the masked form."""
    assert is_valid_caepf(mask_caepf(str_value)) is True


@pytest.mark.parametrize("str_value", LIST_INVALID)
def test_is_valid_caepf_invalid_returns_false(str_value: str) -> None:
    """Reject bad DVs, a ``000`` sequential, an all-equal base and bad lengths."""
    assert is_valid_caepf(str_value) is False


def test_is_valid_caepf_non_str_raises_type_error() -> None:
    """A non-str input is a caller bug the runtime type checker rejects."""
    with pytest.raises(TypeError):
        is_valid_caepf(11144477700154)  # type: ignore[arg-type]


def test_compute_dvs_serpro_sample_is_71() -> None:
    """The ``+ 12`` formula yields DV 71 for the SERPRO sample payload."""
    assert _compute_dvs("000000025001") == "71"


def test_compute_dvs_wraps_past_99_to_00() -> None:
    """A raw 88 plus 12 is 100, which wraps to 00."""
    assert _compute_dvs("123456789001") == "00"


def test_unmask_caepf_float_tail_stripped() -> None:
    """The float ``.0`` tail is dropped."""
    assert unmask_caepf("11144477700154.0") == "11144477700154"


def test_unmask_caepf_punctuation_stripped() -> None:
    """Punctuation is removed."""
    assert unmask_caepf("111.444.777/001-54") == "11144477700154"


def test_unmask_caepf_short_digits_padded() -> None:
    """Digit-only input is left-padded with zeros to 14."""
    assert unmask_caepf("2500171") == "00000002500171"


def test_unmask_caepf_no_digits_returns_empty() -> None:
    """Input with no digits yields an empty string."""
    assert unmask_caepf("abc") == ""


def test_mask_caepf_fourteen_digits_punctuated() -> None:
    """A 14-digit value gets the ``NNN.NNN.NNN/NNN-NN`` mask."""
    assert mask_caepf("11144477700154") == "111.444.777/001-54"


def test_mask_caepf_thirteen_digits_is_padded_then_masked() -> None:
    """A 13-digit value is zero-padded to 14, as with CPF."""
    assert mask_caepf("1114447770015") == "011.144.477/700-15"


def test_mask_caepf_too_long_returns_bare() -> None:
    """More than 14 digits comes back unmasked."""
    assert mask_caepf("111444777001540") == "111444777001540"


def test_mask_caepf_empty_returns_empty() -> None:
    """Empty input stays empty."""
    assert mask_caepf("") == ""
