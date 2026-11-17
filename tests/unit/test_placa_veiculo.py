"""Unit tests for the vehicle plate helpers."""

import pytest

from pure_docs_br import is_valid_placa, mask_placa, unmask_placa


@pytest.mark.parametrize("str_value", ["ABC1234", "abc-1234", "ABC1D23", "BRA2E19"])
def test_is_valid_placa_valid_format_returns_true(str_value: str) -> None:
    """The issue's valid examples pass."""
    assert is_valid_placa(str_value) is True


@pytest.mark.parametrize(
    "str_value",
    ["ABC123", "AB12345", "ABC12D4", "1BC1234", "ABCD123", ""],
)
def test_is_valid_placa_invalid_format_returns_false(str_value: str) -> None:
    """The issue's invalid examples return False without raising."""
    assert is_valid_placa(str_value) is False


@pytest.mark.parametrize("str_value", ["ＡＢＣ1234", "ABC１２３４", "ABC1Ｄ23"])
def test_is_valid_placa_full_width_returns_false(str_value: str) -> None:
    """Full-width letters and digits are never accepted."""
    assert is_valid_placa(str_value) is False


def test_unmask_placa_lower_hyphenated_returns_upper_bare() -> None:
    """Lower case and the hyphen are normalised."""
    assert unmask_placa("abc-1234") == "ABC1234"


def test_unmask_placa_full_width_characters_are_dropped() -> None:
    """Full-width letters and digits are filtered out, not kept."""
    assert unmask_placa("ＡＢＣ-１２３４") == ""


def test_unmask_placa_keeps_no_padding() -> None:
    """A short value is not zero padded."""
    assert unmask_placa("ab12") == "AB12"


def test_mask_placa_old_format_adds_hyphen() -> None:
    """The old format is written ABC-1234."""
    assert mask_placa("ABC1234") == "ABC-1234"


def test_mask_placa_mercosul_has_no_separator() -> None:
    """The Mercosul format keeps no separator."""
    assert mask_placa("ABC1D23") == "ABC1D23"


def test_mask_placa_no_format_returns_unmasked_value() -> None:
    """A value that fits neither format is returned unmasked."""
    assert mask_placa("AB12") == "AB12"


@pytest.mark.parametrize("fn_call", [is_valid_placa, mask_placa, unmask_placa])
def test_placa_functions_non_str_raise_type_error(fn_call: object) -> None:
    """A non-``str`` input raises ``TypeError`` from the type checker."""
    with pytest.raises(TypeError):
        fn_call(None)  # type: ignore[operator]
