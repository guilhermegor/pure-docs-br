"""Unit tests for the deprecated ``pure_docs_br.br_identifiers`` shim."""

import importlib
import subprocess
import sys

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


def test_package_attribute_access_lazily_imports_shim_and_warns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``pure_docs_br.br_identifiers`` still resolves, and warns, as it did before the split."""
    monkeypatch.delitem(sys.modules, "pure_docs_br.br_identifiers", raising=False)
    monkeypatch.delattr(pure_docs_br, "br_identifiers", raising=False)
    with pytest.warns(DeprecationWarning, match=r"2\.0\.0"):
        pure_docs_br.br_identifiers  # noqa: B018 - attribute access is the behaviour under test


def test_package_import_never_touches_the_deprecated_shim() -> None:
    """``import pure_docs_br`` raises no package-scoped ``DeprecationWarning``."""
    cls_result = subprocess.run(  # noqa: S603 - constant argv, no untrusted input
        [
            sys.executable,
            "-W",
            "error::DeprecationWarning:pure_docs_br",
            "-c",
            "import pure_docs_br",
        ],
        check=False,
    )
    assert cls_result.returncode == 0
