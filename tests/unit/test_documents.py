"""Unit tests for the per-document strategy registry."""

import pytest

import purepii_br
from purepii_br import DICT_DOCUMENTS, DocumentStrategy


LIST_PLAIN: list[str] = [
    "boleto_arrecadacao",
    "boleto_cobranca",
    "caepf",
    "cep",
    "certidao_matricula",
    "chave_acesso",
    "cnh",
    "cnpj",
    "cns",
    "cpf",
    "pis_pasep",
    "placa",
    "processo_cnj",
    "renavam",
    "rg",
    "titulo_eleitor",
]
LIST_UFS: list[str] = [
    "ac", "al", "ap", "am", "ba", "ce", "df", "es", "go", "ma", "mt", "ms", "mg", "pa",
    "pb", "pr", "pe", "pi", "rj", "rn", "rs", "ro", "rr", "sc", "sp", "se", "to",
]  # fmt: skip
LIST_IE: list[str] = [f"inscricao_estadual_{str_uf}" for str_uf in LIST_UFS]
LIST_NAMES: list[str] = sorted([*LIST_PLAIN, "cin", *LIST_IE])
LIST_MASKLESS: list[str] = ["cin", "cnh", "renavam", "rg"]
LIST_MASKED: list[str] = [str_n for str_n in LIST_PLAIN if str_n not in LIST_MASKLESS]


def test_registry_keys_are_the_document_names() -> None:
    """The registry holds exactly the documents with a uniform call shape."""
    assert sorted(DICT_DOCUMENTS) == LIST_NAMES


@pytest.mark.parametrize("str_name", LIST_PLAIN)
def test_strategy_is_valid_is_the_public_function(str_name: str) -> None:
    """Each strategy wraps the module-level validator, never a copy."""
    assert DICT_DOCUMENTS[str_name].is_valid is getattr(purepii_br, f"is_valid_{str_name}")


@pytest.mark.parametrize("str_name", LIST_PLAIN)
def test_strategy_unmask_is_the_public_function(str_name: str) -> None:
    """Each strategy wraps the module-level unmasker, never a copy."""
    assert DICT_DOCUMENTS[str_name].unmask is getattr(purepii_br, f"unmask_{str_name}")


@pytest.mark.parametrize("str_name", LIST_MASKED)
def test_strategy_mask_is_the_public_mask(str_name: str) -> None:
    """Documents with an official mask expose the real ``mask_*``."""
    assert DICT_DOCUMENTS[str_name].mask is getattr(purepii_br, f"mask_{str_name}")


@pytest.mark.parametrize("str_name", LIST_MASKLESS)
def test_maskless_document_returns_unmasked_digits(str_name: str) -> None:
    """A document with no official mask returns the unmasked digits and never raises."""
    cls_strategy = DICT_DOCUMENTS[str_name]
    assert cls_strategy.mask("0265.030.6461") == cls_strategy.unmask("0265.030.6461")


def test_cin_strategy_is_valid_is_the_public_function() -> None:
    """The CIN strategy wraps the public CIN validator."""
    assert DICT_DOCUMENTS["cin"].is_valid is purepii_br.is_valid_cin


def test_cin_strategy_unmask_is_the_rg_unmasker() -> None:
    """The CIN number is a CPF, so the RG unmasker is its normaliser."""
    assert DICT_DOCUMENTS["cin"].unmask is purepii_br.unmask_rg


def test_cin_strategy_accepts_a_valid_cpf_number() -> None:
    """A CIN validates through the CPF rule."""
    assert DICT_DOCUMENTS["cin"].is_valid("529.982.247-25") is True


def test_rg_strategy_uses_the_generic_rule_without_uf() -> None:
    """The RG strategy validates with the UF-less rule."""
    assert DICT_DOCUMENTS["rg"].is_valid("12.345.678-9") is True


@pytest.mark.parametrize("str_name", LIST_IE)
def test_ie_strategy_is_valid_binds_the_uf(str_name: str) -> None:
    """Each per-UF IE validator is a partial of the public one with its own UF."""
    cls_valid = DICT_DOCUMENTS[str_name].is_valid
    assert (
        (cls_valid.func, cls_valid.keywords)
        == (  # type: ignore[attr-defined]
            purepii_br.is_valid_inscricao_estadual,
            {"str_uf": str_name[-2:].upper()},
        )
    )


@pytest.mark.parametrize("str_name", LIST_IE)
def test_ie_strategy_mask_binds_the_uf(str_name: str) -> None:
    """Each per-UF IE mask is a partial of the public one with its own UF."""
    cls_mask = DICT_DOCUMENTS[str_name].mask
    assert (
        (cls_mask.func, cls_mask.keywords)
        == (  # type: ignore[attr-defined]
            purepii_br.mask_inscricao_estadual,
            {"str_uf": str_name[-2:].upper()},
        )
    )


@pytest.mark.parametrize("str_name", LIST_IE)
def test_ie_strategy_unmask_is_the_public_function(str_name: str) -> None:
    """The IE unmasker needs no UF, so it is the plain public function."""
    assert DICT_DOCUMENTS[str_name].unmask is purepii_br.unmask_inscricao_estadual


def test_ie_sp_strategy_is_valid_accepts_official_example() -> None:
    """The SP entry validates the official SP example."""
    assert DICT_DOCUMENTS["inscricao_estadual_sp"].is_valid("110.042.490.114") is True


def test_ie_sp_strategy_mask_formats() -> None:
    """The SP entry masks with the SP mask."""
    assert DICT_DOCUMENTS["inscricao_estadual_sp"].mask("110042490114") == "110.042.490.114"


def test_cpf_strategy_mask_formats() -> None:
    """The uniform interface masks through the public function."""
    assert DICT_DOCUMENTS["cpf"].mask("52998224725") == "529.982.247-25"


def test_cpf_strategy_is_valid_accepts_masked() -> None:
    """The uniform interface validates through the public function."""
    assert DICT_DOCUMENTS["cpf"].is_valid("529.982.247-25") is True


def test_cpf_strategy_unmask_strips() -> None:
    """The uniform interface unmasks through the public function."""
    assert DICT_DOCUMENTS["cpf"].unmask("529.982.247-25") == "52998224725"


def test_unknown_document_raises_key_error() -> None:
    """An unregistered name is a KeyError, never a silent default."""
    with pytest.raises(KeyError):
        DICT_DOCUMENTS["unknown"]


def test_strategy_is_frozen() -> None:
    """A strategy is immutable."""
    with pytest.raises(AttributeError):
        DICT_DOCUMENTS["cpf"].mask = str  # type: ignore[misc]


@pytest.mark.parametrize("str_name", ["DICT_DOCUMENTS", "DocumentStrategy"])
def test_public_api_exports_registry_names(str_name: str) -> None:
    """The public API lists the registry and its strategy type."""
    assert str_name in purepii_br.__all__


def test_registry_values_are_strategies() -> None:
    """Every registered value is a DocumentStrategy."""
    assert all(isinstance(cls_s, DocumentStrategy) for cls_s in DICT_DOCUMENTS.values())
