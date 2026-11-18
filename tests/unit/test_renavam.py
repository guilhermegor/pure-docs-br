"""Unit tests for the RENAVAM helpers."""

import pytest

from pure_docs_br import is_valid_renavam, unmask_renavam
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
