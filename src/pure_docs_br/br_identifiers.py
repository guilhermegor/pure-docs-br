"""Deprecated alias of :mod:`pure_docs_br.cpf` and :mod:`pure_docs_br.cnpj`.

Importing this module emits a ``DeprecationWarning``; it will be removed in 2.0.0. Import
from the package root (``from pure_docs_br import is_valid_cpf``) or from ``pure_docs_br.cpf``
/ ``pure_docs_br.cnpj`` instead.
"""

from __future__ import annotations

import warnings

from pure_docs_br.cnpj import is_valid_cnpj, mask_cnpj, unmask_cnpj
from pure_docs_br.cpf import is_valid_cpf, mask_cpf, unmask_cpf


warnings.warn(
    "pure_docs_br.br_identifiers is deprecated and will be removed in 2.0.0; "
    "import from pure_docs_br (or pure_docs_br.cpf / pure_docs_br.cnpj) instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "is_valid_cnpj",
    "is_valid_cpf",
    "mask_cnpj",
    "mask_cpf",
    "unmask_cnpj",
    "unmask_cpf",
]
