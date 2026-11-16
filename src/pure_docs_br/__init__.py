"""pure-docs-br package."""

from importlib.metadata import PackageNotFoundError, version

from .br_identifiers import (
    is_valid_cnpj,
    is_valid_cpf,
    mask_cnpj,
    mask_cpf,
    unmask_cnpj,
    unmask_cpf,
)
from .cep import is_valid_cep, mask_cep, unmask_cep
from .pis_pasep import is_valid_pis_pasep, mask_pis_pasep, unmask_pis_pasep
from .titulo_eleitor import (
    is_valid_titulo_eleitor,
    mask_titulo_eleitor,
    unmask_titulo_eleitor,
)


try:
    __version__ = version("pure-docs-br")
except PackageNotFoundError:  # pragma: no cover - source tree without an installed dist
    __version__ = "0.0.0"


__all__ = [
    "__version__",
    "is_valid_cep",
    "is_valid_cnpj",
    "is_valid_cpf",
    "is_valid_pis_pasep",
    "is_valid_titulo_eleitor",
    "mask_cep",
    "mask_cnpj",
    "mask_cpf",
    "mask_pis_pasep",
    "mask_titulo_eleitor",
    "unmask_cep",
    "unmask_cnpj",
    "unmask_cpf",
    "unmask_pis_pasep",
    "unmask_titulo_eleitor",
]
