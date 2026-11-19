"""Unit tests for the deprecated ``purepii_br.br_identifiers`` shim."""

import importlib
import os
from pathlib import Path
import subprocess
import sys

import pytest

import purepii_br
from purepii_br import br_identifiers


STR_IMPORT_PROGRAM: str = (
    "import sys, purepii_br; sys.exit('purepii_br.br_identifiers' in sys.modules)"
)
LIST_SHIM_PROGRAMS: list[str] = [
    "import purepii_br; purepii_br.br_identifiers",
    "from purepii_br import br_identifiers",
    "import purepii_br.br_identifiers",
]


def _run_child(*tuple_args: str) -> subprocess.CompletedProcess[str]:
    """Run ``python *tuple_args`` in a fresh interpreter importing this copy of the package."""
    path_pkg_root = Path(purepii_br.__file__).parents[1]
    str_pythonpath = os.pathsep.join(
        filter(None, [str(path_pkg_root), os.environ.get("PYTHONPATH")])
    )
    dict_env = {**os.environ, "PYTHONPATH": str_pythonpath}
    dict_env.pop("PYTHONWARNINGS", None)
    dict_env.pop("PYTHONDEVMODE", None)
    return subprocess.run(  # noqa: S603 - constant argv, no untrusted input
        [sys.executable, *tuple_args],
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
    assert getattr(br_identifiers, str_name) is getattr(purepii_br, str_name)


def test_package_attribute_access_lazily_imports_shim_and_warns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``purepii_br.br_identifiers`` still resolves, and warns, as it did before the split."""
    monkeypatch.delitem(sys.modules, "purepii_br.br_identifiers", raising=False)
    monkeypatch.delattr(purepii_br, "br_identifiers", raising=False)
    with pytest.warns(DeprecationWarning, match=r"2\.0\.0"):
        purepii_br.br_identifiers  # noqa: B018 - attribute access is the behaviour under test


def test_package_import_never_touches_the_deprecated_shim() -> None:
    """``import purepii_br`` never imports the shim, from any submodule or by any route."""
    cls_result = _run_child("-c", STR_IMPORT_PROGRAM)
    assert cls_result.returncode == 0, cls_result.stderr


@pytest.mark.parametrize("str_program", LIST_SHIM_PROGRAMS)
def test_shim_warning_is_shown_under_default_filters(str_program: str) -> None:
    """A ``__main__`` importer sees the warning without ``-W``: it is attributed to the caller."""
    cls_result = _run_child("-c", str_program)
    assert "<string>:1: DeprecationWarning: purepii_br.br_identifiers" in cls_result.stderr, (
        f"exit {cls_result.returncode}: {cls_result.stderr}"
    )


def test_shim_warning_counts_an_importer_whose_name_contains_bootstrap(tmp_path: Path) -> None:
    """An importer named ``app_bootstrap.py`` still gets the warning attributed to its own line."""
    path_script = tmp_path / "app_bootstrap.py"
    path_script.write_text("import purepii_br.br_identifiers\n", encoding="utf-8")
    cls_result = _run_child(str(path_script))
    assert "app_bootstrap.py:1: DeprecationWarning" in cls_result.stderr, cls_result.stderr
