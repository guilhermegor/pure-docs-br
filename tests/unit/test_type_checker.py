"""Unit tests for the dependency-free runtime type checker."""

import importlib
from typing import TYPE_CHECKING

import pytest

from purepii_br import mask_cpf, unmask_cnpj
from purepii_br._internal.utils.typing import type_checker


if TYPE_CHECKING:
    from decimal import Decimal


@pytest.mark.parametrize("fn_target", [mask_cpf, unmask_cnpj])
@pytest.mark.parametrize("value", [None, 1, 1.5, b"52998224725"])
def test_public_function_non_str_argument_raises_type_error(*, fn_target, value) -> None:  # noqa: ANN001
    """A non-``str`` argument is rejected with ``TypeError``, as the original checker did."""
    with pytest.raises(TypeError):
        fn_target(value)


@type_checker
def _probe_keyword(*, int_value: int) -> int:
    """Return the value unchanged."""
    return int_value


@type_checker
def _probe_generic(tuple_value: tuple[int, ...]) -> int:
    """Return the tuple length."""
    return len(tuple_value)


def test_type_checker_keyword_argument_is_checked() -> None:
    """An annotated keyword-only argument is validated like a positional one."""
    with pytest.raises(TypeError):
        _probe_keyword(int_value="1")


def test_type_checker_generic_annotation_is_left_to_mypy() -> None:
    """A generic annotation is not enforced at runtime."""
    assert _probe_generic((1, 2)) == 2


def test_type_checker_preserves_function_metadata() -> None:
    """The wrapper keeps the wrapped function's name and docstring."""
    assert mask_cpf.__name__ == "mask_cpf"


@type_checker
def _probe_type_checking_only(value: "Decimal") -> int:
    """Annotate with a name imported only for the type checker."""
    return 1


@type_checker
def _probe_var_positional(*tuple_values: int) -> int:
    """Return the sum of the positional values."""
    return sum(tuple_values)


@type_checker
def _probe_var_keyword(**dict_values: str) -> int:
    """Return how many keyword values were passed."""
    return len(dict_values)


@type_checker
def _probe_float(float_value: float) -> float:
    """Return the value unchanged."""
    return float_value


def test_type_checker_type_checking_only_annotation_imports_and_runs() -> None:
    """An annotation naming a ``TYPE_CHECKING``-only import neither breaks import nor the call."""
    assert _probe_type_checking_only(1) == 1


def test_type_checker_var_positional_checks_each_element() -> None:
    """``*args: int`` accepts several ints instead of rejecting the tuple."""
    assert _probe_var_positional(1, 2) == 3


def test_type_checker_var_positional_rejects_a_bad_element() -> None:
    """``*args: int`` still rejects one element of the wrong type."""
    with pytest.raises(TypeError):
        _probe_var_positional(1, 2.5)


def test_type_checker_var_keyword_checks_each_value() -> None:
    """``**kw: str`` accepts str values instead of rejecting the dict."""
    assert _probe_var_keyword(a="x", b="y") == 2


def test_type_checker_var_keyword_rejects_a_bad_value() -> None:
    """``**kw: str`` still rejects one value of the wrong type."""
    with pytest.raises(TypeError):
        _probe_var_keyword(a="x", b=1)


def test_type_checker_int_is_accepted_where_float_is_annotated() -> None:
    """``int`` widens to ``float``, as PEP 484 and mypy allow."""
    assert _probe_float(1) == 1.0


@type_checker
def _probe_mixed(*, int_value: int, value: "Decimal") -> int:
    """Mix a plain annotation with a ``TYPE_CHECKING``-only one."""
    return int_value


def test_type_checker_unavailable_hint_keeps_checking_the_others() -> None:
    """A ``TYPE_CHECKING``-only annotation does not switch off the plain ``int`` check."""
    with pytest.raises(TypeError):
        _probe_mixed(int_value="1", value=2)


def _probe_plain(int_value: int) -> int:
    """Return the value unchanged; decorated inside the test that needs it."""
    return int_value


def test_type_checker_resolves_hints_once_per_function(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hints are resolved on the first call only, then reused from the cache."""
    cls_module = importlib.import_module("purepii_br._internal.utils.typing.type_checker")
    fn_real = cls_module._resolve_hints
    list_calls: list[object] = []
    monkeypatch.setattr(
        cls_module, "_resolve_hints", lambda fn: list_calls.append(fn) or fn_real(fn)
    )
    fn_probe = type_checker(_probe_plain)
    fn_probe(1)
    fn_probe(2)
    assert len(list_calls) == 1


def test_type_checker_bool_is_rejected_where_int_is_annotated() -> None:
    """``True`` is not accepted for an ``int`` parameter."""
    with pytest.raises(TypeError):
        _probe_keyword(int_value=True)
