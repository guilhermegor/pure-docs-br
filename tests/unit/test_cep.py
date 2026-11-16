"""Unit tests for the CEP helpers."""

import pytest

from pure_docs_br import is_valid_cep, mask_cep, unmask_cep


@pytest.mark.parametrize("str_value", ["01001-000", "01001010", "11099999", "1001000"])
def test_is_valid_cep_valid_format_returns_true(str_value: str) -> None:
    """The issue's valid examples, with and without mask, pass."""
    assert is_valid_cep(str_value) is True


@pytest.mark.parametrize("str_value", ["010010000", "ABCDE-FGH", "", "123456789"])
def test_is_valid_cep_invalid_format_returns_false(str_value: str) -> None:
    """The issue's invalid examples return False without raising."""
    assert is_valid_cep(str_value) is False


def test_is_valid_cep_all_zeros_returns_true() -> None:
    """The all-zeros CEP passes the format check (documented decision)."""
    assert is_valid_cep("00000-000") is True


def test_unmask_cep_masked_value_returns_bare_digits() -> None:
    """A punctuated CEP unmasks to its 8 digits."""
    assert unmask_cep("01001-000") == "01001000"


def test_unmask_cep_float_artifact_pads_leading_zero() -> None:
    """A float-to-str ``.0`` tail is dropped and the lost zero restored."""
    assert unmask_cep("1001000.0") == "01001000"


def test_unmask_cep_empty_returns_empty() -> None:
    """An empty input yields an empty string."""
    assert unmask_cep("") == ""


def test_mask_cep_bare_value_returns_masked() -> None:
    """A bare 8-digit CEP is formatted as XXXXX-XXX."""
    assert mask_cep("01001000") == "01001-000"


def test_mask_cep_short_value_restores_zero_then_masks() -> None:
    """A 7-digit CEP is zero-padded before masking."""
    assert mask_cep("1001000") == "01001-000"


def test_mask_cep_too_long_returns_unmasked_value() -> None:
    """A 9-digit value is returned without a mask."""
    assert mask_cep("123456789") == "123456789"


@pytest.mark.parametrize("fn_call", [is_valid_cep, mask_cep, unmask_cep])
def test_cep_functions_non_str_raise_type_error(fn_call: object) -> None:
    """A non-``str`` input raises ``TypeError`` from the type checker."""
    with pytest.raises(TypeError):
        fn_call(None)  # type: ignore[operator]
