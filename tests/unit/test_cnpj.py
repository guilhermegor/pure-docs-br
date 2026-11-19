"""Unit tests for the CNPJ helpers."""

from decimal import Decimal

import pytest

from purepii_br import is_valid_cnpj, mask_cnpj, unmask_cnpj


def test_unmask_cnpj_masked_value_returns_bare_digits() -> None:
    """A punctuated CNPJ unmasks to its 14 bare digits."""
    assert unmask_cnpj("11.222.333/0001-81") == "11222333000181"


def test_unmask_cnpj_float_artifact_drops_trailing_zero_decimal() -> None:
    """A float→str ``.0`` tail is stripped before normalisation."""
    assert unmask_cnpj("11222333000181.0") == "11222333000181"


def test_unmask_cnpj_short_numeric_left_zero_pads_to_14() -> None:
    """A short purely-numeric CNPJ is left-zero-padded to 14."""
    assert unmask_cnpj("1222333000181") == "01222333000181"


def test_unmask_cnpj_alphanumeric_uppercases_and_keeps_letters() -> None:
    """An alphanumeric CNPJ is uppercased with letters preserved."""
    assert unmask_cnpj("12.abc.345/01de-35") == "12ABC34501DE35"


def test_unmask_cnpj_empty_returns_empty() -> None:
    """An empty input yields an empty string."""
    assert unmask_cnpj("") == ""


def test_mask_cnpj_bare_value_returns_punctuated() -> None:
    """A bare CNPJ is formatted as ``XX.XXX.XXX/XXXX-XX``."""
    assert mask_cnpj("11222333000181") == "11.222.333/0001-81"


def test_mask_cnpj_invalid_length_passes_through_unmasked() -> None:
    """An alphanumeric value that cannot reach 14 chars passes through unmasked.

    A short *numeric* value is left-zero-padded to 14 by ``unmask_cnpj`` and then
    masked, so the pass-through branch only triggers for non-14 alphanumeric input.
    """
    assert mask_cnpj("12ABC") == "12ABC"


def test_is_valid_cnpj_legacy_numeric_true() -> None:
    """A correct legacy numeric CNPJ validates."""
    assert is_valid_cnpj("11.222.333/0001-81") is True


def test_is_valid_cnpj_alphanumeric_2026_format_true() -> None:
    """The official 2026 alphanumeric CNPJ example validates."""
    assert is_valid_cnpj("12.ABC.345/01DE-35") is True


def test_is_valid_cnpj_wrong_check_digit_false() -> None:
    """A CNPJ with a wrong check digit is rejected."""
    assert is_valid_cnpj("11222333000182") is False


def test_is_valid_cnpj_all_zeros_false() -> None:
    """An all-zeros CNPJ is rejected."""
    assert is_valid_cnpj("00000000000000") is False


def test_is_valid_cnpj_wrong_length_false() -> None:
    """A CNPJ of the wrong length is rejected."""
    assert is_valid_cnpj("112223330001") is False


def test_is_valid_cnpj_serpro_example_bare_form_true() -> None:
    """The Serpro worked example validates in its bare form.

    Base ``12ABC34501DE`` has a first-digit weighted sum of 459 (459 mod 11 = 8, DV1 = 3)
    and a second-digit sum of 424 (424 mod 11 = 6, DV2 = 5), giving ``12ABC34501DE35``.
    Source: https://www.serpro.gov.br/menu/noticias/videos/calculodvcnpjalfanaumerico.pdf
    """
    assert is_valid_cnpj("12ABC34501DE35") is True


def test_is_valid_cnpj_receita_example_lowercase_masked_true() -> None:
    """The Receita Federal worked example validates when typed in lowercase.

    Source: https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/perguntas-e-respostas/cnpj/cnpj-alfanumerico.pdf
    """
    assert is_valid_cnpj("12.abc.345/01de-35") is True


@pytest.mark.parametrize("str_cnpj", ["12ABC34501DE30", "12ABC34501DE34", "12ABC34501DE45"])
def test_is_valid_cnpj_serpro_example_wrong_check_digit_false(str_cnpj: str) -> None:
    """Changing either official check digit of the Serpro example is rejected.

    Source: https://www.serpro.gov.br/menu/noticias/videos/calculodvcnpjalfanaumerico.pdf
    """
    assert is_valid_cnpj(str_cnpj) is False


def test_mask_cnpj_alphanumeric_returns_punctuated() -> None:
    """The official alphanumeric example is masked as ``XX.XXX.XXX/XXXX-XX``.

    Source: https://www.serpro.gov.br/menu/noticias/videos/calculodvcnpjalfanaumerico.pdf
    """
    assert mask_cnpj("12ABC34501DE35") == "12.ABC.345/01DE-35"


def test_is_valid_cnpj_short_input_is_zero_padded_true() -> None:
    """``"191"`` pads to 14 digits whose check digits happen to be right (pinned behaviour)."""
    assert is_valid_cnpj("191") is True


@pytest.mark.parametrize("fn_call", [is_valid_cnpj, unmask_cnpj])
@pytest.mark.parametrize("obj_value", [None, Decimal("1.5"), 52998224725])
def test_functions_non_str_raise_type_error(*, fn_call: object, obj_value: object) -> None:
    """Every CNPJ function rejects a non-``str`` with ``TypeError``."""
    with pytest.raises(TypeError):
        fn_call(obj_value)  # type: ignore[operator]


@pytest.mark.parametrize(
    ("fn_call", "str_value"),
    [
        (mask_cnpj, ""),
        (mask_cnpj, "12ABC"),
        (mask_cnpj, "123456789012345"),
    ],
)
def test_mask_not_document_length_returns_unmasked_value(
    *, fn_call: object, str_value: str
) -> None:
    """``mask_cnpj`` returns the unmasked value when empty, too long or short."""
    assert fn_call(str_value) == str_value  # type: ignore[operator]


@pytest.mark.parametrize("fn_call", [is_valid_cnpj])
def test_is_valid_empty_str_false(fn_call: object) -> None:
    """An empty string is invalid, not an error."""
    assert fn_call("") is False  # type: ignore[operator]


def test_unmask_cnpj_scientific_notation_is_not_handled() -> None:
    """Scientific notation is not a float artifact: the exponent letter is kept."""
    assert unmask_cnpj("1.1222333000181e+13") == "11222333000181E13"


LIST_NON_ASCII_CNPJ: list[str] = ["١١٢٢٢٣٣٣٠٠٠١٨١", "１１２２２３３３０００１８１"]


@pytest.mark.parametrize("str_value", LIST_NON_ASCII_CNPJ)
def test_unmask_cnpj_non_ascii_digits_returns_empty(str_value: str) -> None:
    """Arabic-Indic and full-width digits are dropped, never kept."""
    assert unmask_cnpj(str_value) == ""


@pytest.mark.parametrize("str_value", LIST_NON_ASCII_CNPJ)
def test_is_valid_cnpj_non_ascii_digits_returns_false(str_value: str) -> None:
    """Arabic-Indic and full-width digits are not a valid CNPJ."""
    assert is_valid_cnpj(str_value) is False
