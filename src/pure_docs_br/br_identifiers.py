"""Deprecated alias of :mod:`pure_docs_br.cpf` and :mod:`pure_docs_br.cnpj`.

Importing this module emits a ``DeprecationWarning``; it will be removed in 2.0.0. Import
from the package root (``from pure_docs_br import is_valid_cpf``) or from ``pure_docs_br.cpf``
/ ``pure_docs_br.cnpj`` instead.
"""

from __future__ import annotations

import importlib
from pathlib import Path
import sys
from traceback import walk_stack
from types import FrameType
import warnings

from pure_docs_br._internal.utils.typing import type_checker
from pure_docs_br.cnpj import is_valid_cnpj, mask_cnpj, unmask_cnpj
from pure_docs_br.cpf import is_valid_cpf, mask_cpf, unmask_cpf


_PATH_IMPORTLIB: Path = Path(importlib.__file__).parent


@type_checker
def _is_skipped_by_warn(str_file: str) -> bool:
    """Tell whether :func:`warnings.warn` itself skips a frame from ``str_file``.

    Mirrors CPython's ``_is_internal_filename``: both ``importlib`` and ``_bootstrap`` must
    appear, so an importer such as ``app_bootstrap.py`` is still counted.

    Parameters
    ----------
    str_file : str
        A frame's ``co_filename``.

    Returns
    -------
    bool
        ``True`` when ``warnings.warn`` leaves this frame out of the ``stacklevel`` count.
    """
    return "importlib" in str_file and "_bootstrap" in str_file


@type_checker
def _is_internal_frame(cls_frame: FrameType) -> bool:
    """Tell whether ``cls_frame`` belongs to importlib or to this package.

    Parameters
    ----------
    cls_frame : FrameType
        A frame on the import stack.

    Returns
    -------
    bool
        ``True`` for an importlib or ``pure_docs_br`` frame, ``False`` for the importer.
    """
    str_file = cls_frame.f_code.co_filename
    str_module = str(cls_frame.f_globals.get("__name__", ""))
    return (
        str_file.startswith("<frozen importlib")
        or Path(str_file).parent == _PATH_IMPORTLIB
        or str_module.split(".", maxsplit=1)[0] == "pure_docs_br"
    )


@type_checker
def _external_stacklevel(cls_frame: FrameType) -> int:
    """Return the ``stacklevel`` that attributes a warning to the module importing the shim.

    A fixed ``stacklevel=2`` lands on an importlib frame, so Python's default filters (which
    show a ``DeprecationWarning`` only when attributed to ``__main__``) hide it. Frames from
    ``importlib._bootstrap`` are left out of the count, because :func:`warnings.warn` skips
    them itself.

    Parameters
    ----------
    cls_frame : FrameType
        The shim's own module frame, which counts as ``stacklevel=1``.

    Returns
    -------
    int
        The ``stacklevel`` to pass to :func:`warnings.warn` from this module's top level.
    """
    list_counted = [
        cls_f
        for cls_f, _ in walk_stack(cls_frame)
        if not _is_skipped_by_warn(cls_f.f_code.co_filename)
    ]
    return next(
        (int_i + 1 for int_i, cls_f in enumerate(list_counted) if not _is_internal_frame(cls_f)),
        len(list_counted),
    )


warnings.warn(
    "pure_docs_br.br_identifiers is deprecated and will be removed in 2.0.0; "
    "import from pure_docs_br (or pure_docs_br.cpf / pure_docs_br.cnpj) instead.",
    DeprecationWarning,
    stacklevel=_external_stacklevel(sys._getframe()),  # noqa: SLF001
)

__all__ = [
    "is_valid_cnpj",
    "is_valid_cpf",
    "mask_cnpj",
    "mask_cpf",
    "unmask_cnpj",
    "unmask_cpf",
]
