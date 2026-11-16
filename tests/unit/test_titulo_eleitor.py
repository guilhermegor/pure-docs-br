"""Unit tests for the Título de Eleitor helpers."""

import pytest

from pure_docs_br import (
    is_valid_titulo_eleitor,
    mask_titulo_eleitor,
    unmask_titulo_eleitor,
)


LIST_VALID: list[str] = [
    "004356870906",
    "123456780396",
    "876543210124",
    "111111112801",
    "000000000116",
    "000000120248",
]


@pytest.mark.parametrize("str_value", LIST_VALID)
def test_is_valid_titulo_eleitor_valid_returns_true(str_value: str) -> None:
    """The issue's valid examples pass."""
    assert is_valid_titulo_eleitor(str_value) is True


def test_is_valid_titulo_eleitor_spaced_returns_true() -> None:
    """The Wikipedia spaced form passes."""
    assert is_valid_titulo_eleitor("0043 5687 09 06") is True


@pytest.mark.parametrize(
    "str_value",
    ["123456780397", "123456780296", "123456782996", "1234567803961", "", "ABCDEFGHIJKL"],
)
def test_is_valid_titulo_eleitor_invalid_returns_false(str_value: str) -> None:
    """The issue's invalid examples return False without raising."""
    assert is_valid_titulo_eleitor(str_value) is False


LIST_EACH_UF: list[str] = [
    "123456780191",
    "123456780299",
    "123456780396",
    "123456780493",
    "123456780590",
    "123456780698",
    "123456780795",
    "123456780892",
    "123456780990",
    "123456781090",
    "123456781198",
    "123456781295",
    "123456781392",
    "123456781490",
    "123456781597",
    "123456781694",
    "123456781791",
    "123456781899",
    "123456781996",
    "123456782097",
    "123456782194",
    "123456782291",
    "123456782399",
    "123456782496",
    "123456782593",
    "123456782690",
    "123456782798",
    "123456782895",
]

LIST_UNKNOWN_UF: list[str] = [
    "123456780094",
    "123456782992",
]


@pytest.mark.parametrize("str_value", LIST_EACH_UF)
def test_is_valid_titulo_eleitor_each_uf_returns_true(str_value: str) -> None:
    """All 28 UF codes are accepted."""
    assert is_valid_titulo_eleitor(str_value) is True


@pytest.mark.parametrize("str_value", LIST_UNKNOWN_UF)
def test_is_valid_titulo_eleitor_unknown_uf_returns_false(str_value: str) -> None:
    """UF codes 00 and 29 are rejected even with matching check digits."""
    assert is_valid_titulo_eleitor(str_value) is False


def test_unmask_titulo_eleitor_float_artifact_pads_zeros() -> None:
    """The float tail is dropped and leading zeros restored."""
    assert unmask_titulo_eleitor("4356870906.0") == "004356870906"


def test_unmask_titulo_eleitor_empty_returns_empty() -> None:
    """Empty input yields an empty string."""
    assert unmask_titulo_eleitor("") == ""


def test_mask_titulo_eleitor_bare_value_returns_masked() -> None:
    """A 12-digit title is grouped by 4."""
    assert mask_titulo_eleitor("004356870906") == "0043 5687 0906"


def test_mask_titulo_eleitor_too_long_returns_unmasked_value() -> None:
    """A 13-digit value is returned without a mask."""
    assert mask_titulo_eleitor("1234567803961") == "1234567803961"


@pytest.mark.parametrize(
    "fn_call", [is_valid_titulo_eleitor, mask_titulo_eleitor, unmask_titulo_eleitor]
)
def test_titulo_eleitor_functions_non_str_raise_type_error(fn_call: object) -> None:
    """A non-``str`` input raises ``TypeError`` from the type checker."""
    with pytest.raises(TypeError):
        fn_call(None)  # type: ignore[operator]
