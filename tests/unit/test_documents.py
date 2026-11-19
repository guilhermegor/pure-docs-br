"""Unit tests for the per-document strategy registry."""

import pytest

import purepii_br
from purepii_br import DICT_DOCUMENTS, DocumentStrategy


LIST_NAMES: list[str] = [
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
    "titulo_eleitor",
]
LIST_MASKLESS: list[str] = ["cnh", "renavam"]


def test_registry_keys_are_the_document_names() -> None:
    """The registry holds exactly the documents with a uniform call shape."""
    assert sorted(DICT_DOCUMENTS) == LIST_NAMES


@pytest.mark.parametrize("str_name", LIST_NAMES)
def test_strategy_is_valid_is_the_public_function(str_name: str) -> None:
    """Each strategy wraps the module-level validator, never a copy."""
    assert DICT_DOCUMENTS[str_name].is_valid is getattr(purepii_br, f"is_valid_{str_name}")


@pytest.mark.parametrize("str_name", LIST_NAMES)
def test_strategy_unmask_is_the_public_function(str_name: str) -> None:
    """Each strategy wraps the module-level unmasker, never a copy."""
    assert DICT_DOCUMENTS[str_name].unmask is getattr(purepii_br, f"unmask_{str_name}")


@pytest.mark.parametrize("str_name", [s for s in LIST_NAMES if s not in LIST_MASKLESS])
def test_strategy_mask_is_the_public_mask(str_name: str) -> None:
    """Documents with an official mask expose the real ``mask_*``."""
    assert DICT_DOCUMENTS[str_name].mask is getattr(purepii_br, f"mask_{str_name}")


@pytest.mark.parametrize("str_name", LIST_MASKLESS)
def test_maskless_document_returns_unmasked_digits(str_name: str) -> None:
    """A document with no official mask returns the unmasked digits and never raises."""
    strategy = DICT_DOCUMENTS[str_name]
    assert strategy.mask("0265.030.6461") == strategy.unmask("0265.030.6461")


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
