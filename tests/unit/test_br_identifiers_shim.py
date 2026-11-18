"""Unit tests for the deprecated ``pure_docs_br.br_identifiers`` shim."""

import importlib
import os
from pathlib import Path
import subprocess
import sys

import pytest

import pure_docs_br
from pure_docs_br import br_identifiers


STR_IMPORT_PROGRAM: str = (
    "import warnings; "
    "warnings.filterwarnings("
    "'error', message='pure_docs_br.br_identifiers is deprecated', category=DeprecationWarning); "
    "import pure_docs_br"
)
LIST_SHIM_PROGRAMS: list[str] = [
    "import pure_docs_br; pure_docs_br.br_identifiers",
    "from pure_docs_br import br_identifiers",
    "import pure_docs_br.br_identifiers",
]


def _run_child(str_program: str) -> subprocess.CompletedProcess[str]:
    """Run ``str_program`` in a fresh interpreter that imports this same copy of the package."""
    path_pkg_root = Path(pure_docs_br.__file__).parents[1]
    str_pythonpath = os.pathsep.join(
        filter(None, [str(path_pkg_root), os.environ.get("PYTHONPATH")])
    )
    dict_env = {**os.environ, "PYTHONPATH": str_pythonpath}
    dict_env.pop("PYTHONWARNINGS", None)
    return subprocess.run(  # noqa: S603 - constant argv, no untrusted input
        [sys.executable, "-c", str_program],
        check=False,
        capture_output=True,
        text=True,
        env=dict_env,
    )


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
    """``import pure_docs_br`` never imports the shim, from any submodule or by any route."""
    cls_result = _run_child(STR_IMPORT_PROGRAM)
    assert cls_result.returncode == 0, cls_result.stderr


@pytest.mark.parametrize("str_program", LIST_SHIM_PROGRAMS)
def test_shim_warning_is_shown_under_default_filters(str_program: str) -> None:
    """Every route to the shim shows its warning without ``-W``: it is attributed to the caller."""
    cls_result = _run_child(str_program)
    assert "<string>:1: DeprecationWarning: pure_docs_br.br_identifiers" in cls_result.stderr
