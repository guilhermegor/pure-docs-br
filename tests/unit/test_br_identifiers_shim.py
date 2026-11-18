"""Unit tests for the deprecated ``pure_docs_br.br_identifiers`` shim."""

import importlib

import pytest

import pure_docs_br
from pure_docs_br import br_identifiers


def test_br_identifiers_import_warns_deprecation_naming_2_0_0() -> None:
    """Importing the shim emits a ``DeprecationWarning`` that says removal is in 2.0.0."""
    with pytest.warns(DeprecationWarning, match=r"removed in 2\.0\.0"):
        importlib.reload(br_identifiers)


@pytest.mark.parametrize("str_name", br_identifiers.__all__)
def test_br_identifiers_reexports_same_function_as_package_root(str_name: str) -> None:
    """Each re-exported function is the package-root object, not a copy."""
    assert getattr(br_identifiers, str_name) is getattr(pure_docs_br, str_name)
