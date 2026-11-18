"""Unit tests for the RENAVAM helpers."""

import pytest

from pure_docs_br import is_valid_renavam, mask_renavam, unmask_renavam
from pure_docs_br.renavam import _compute_dv


LIST_VALID: list[str] = [
    "22500062413",
    "01234567897",
    "63954178210",
    "00000123455",
    "12345678900",
    "99999999906",
]


def _compute_community_dv(str_base: str) -> str:
    """Community form of the check digit: ``(sum * 10) % 11``, with 10 becoming 0."""
    list_weights = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    int_sum = sum(int(str_d) * int_w for str_d, int_w in zip(str_base, list_weights, strict=True))
    return str((int_sum * 10) % 11 % 10)


@pytest.mark.parametrize("str_value", LIST_VALID)
def test_is_valid_renavam_valid_returns_true(str_value: str) -> None:
    """The issue's valid examples pass."""
    assert is_valid_renavam(str_value) is True


@pytest.mark.parametrize("str_value", LIST_VALID)
def test_is_valid_renavam_spaced_returns_true(str_value: str) -> None:
    """The issue's valid examples pass with spaces and punctuation."""
    assert is_valid_renavam(f" {str_value[:3]}.{str_value[3:]} ") is True


@pytest.mark.parametrize(
    "str_value",
    ["22500062414", "01234567898", "00000000000", "1234567890", "", "ABCDEFGHIJK"],
)
def test_is_valid_renavam_invalid_returns_false(str_value: str) -> None:
    """The issue's invalid examples return False without raising."""
    assert is_valid_renavam(str_value) is False


def test_is_valid_renavam_legacy_nine_digits_returns_true() -> None:
    """The old 9-digit number is padded with zeros to 11 before validating."""
    assert is_valid_renavam("000123455") is True


def test_is_valid_renavam_non_str_raises_type_error() -> None:
    """A non-str argument is rejected by the runtime type checker."""
    with pytest.raises(TypeError):
        is_valid_renavam(22500062413)  # type: ignore[arg-type]


def test_compute_dv_matches_community_form_over_ten_thousand_bases() -> None:
    """Official and community check-digit forms agree on 10^4 bases."""
    list_bases = [f"{int_n:010d}" for int_n in range(10_000)]
    assert [_compute_dv(str_b) for str_b in list_bases] == [
        _compute_community_dv(str_b) for str_b in list_bases
    ]


def test_unmask_renavam_float_tail_stripped_and_padded() -> None:
    """The float ``.0`` tail is dropped and the result is padded to 11."""
    assert unmask_renavam("1234567897.0") == "01234567897"


def test_unmask_renavam_punctuation_stripped() -> None:
    """Punctuation and spaces are removed."""
    assert unmask_renavam("225 000.624-13") == "22500062413"


def test_unmask_renavam_no_digits_returns_empty() -> None:
    """Input with no digits yields an empty string."""
    assert unmask_renavam("ABC") == ""


def test_mask_renavam_applies_pattern() -> None:
    """Each N takes the next digit and other characters are copied."""
    assert mask_renavam("22500062413", str_pattern="NNNNNNNNNN-N") == "2250006241-3"


def test_mask_renavam_unmasks_input_first() -> None:
    """A punctuated input is unmasked before the pattern is applied."""
    assert mask_renavam("225.00062413", str_pattern="NNNNNNNNNN-N") == "2250006241-3"


def test_mask_renavam_keeps_any_separator() -> None:
    """Characters other than N are copied as is."""
    assert mask_renavam("22500062413", str_pattern="N" * 11 + "/") == "22500062413/"


@pytest.mark.parametrize("str_pattern", ["", "NNN", "N" * 10, "N" * 12])
def test_mask_renavam_wrong_slot_count_raises(str_pattern: str) -> None:
    """A pattern without exactly 11 N raises ValueError."""
    with pytest.raises(ValueError, match="exactly 11"):
        mask_renavam("22500062413", str_pattern=str_pattern)


@pytest.mark.parametrize("str_value", ["", "ABC", "123456789012"])
def test_mask_renavam_unmaskable_input_returns_bare_value(str_value: str) -> None:
    """Empty, digitless or over-long input never raises and comes back unmasked."""
    assert mask_renavam(str_value, str_pattern="NNNNNNNNNN-N") == unmask_renavam(str_value)


def test_mask_renavam_non_str_raises_type_error() -> None:
    """A non-str argument is rejected by the runtime type checker."""
    with pytest.raises(TypeError):
        mask_renavam(1, str_pattern="NNNNNNNNNN-N")  # type: ignore[arg-type]


def test_mask_renavam_nine_digits_padded_to_eleven() -> None:
    """The old 9-digit number is padded with zeros to 11 before masking."""
    assert mask_renavam("000123455", str_pattern="NNNNNNNNNN-N") == "0000012345-5"
