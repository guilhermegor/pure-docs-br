"""pure-docs-br package."""

from importlib.metadata import PackageNotFoundError, version

from ._internal.utils.br_identifiers import (
    is_valid_cnpj,
    is_valid_cpf,
    mask_cnpj,
    mask_cpf,
    unmask_cnpj,
    unmask_cpf,
)
from .main import main


try:
    __version__ = version("pure-docs-br")
except PackageNotFoundError:  # pragma: no cover - source tree without an installed dist
    __version__ = "0.0.0"


__all__ = [
    "__version__",
    "is_valid_cnpj",
    "is_valid_cpf",
    "main",
    "mask_cnpj",
    "mask_cpf",
    "unmask_cnpj",
    "unmask_cpf",
]
