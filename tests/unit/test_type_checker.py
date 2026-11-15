"""Unit tests for the dependency-free runtime type checker."""

import pytest

from pure_docs_br import mask_cpf, unmask_cnpj
from pure_docs_br._internal.utils.typing import type_checker


@pytest.mark.parametrize("fn_target", [mask_cpf, unmask_cnpj])
@pytest.mark.parametrize("value", [None, 1, 1.5, b"52998224725"])
def test_public_function_non_str_argument_raises_type_error(fn_target, value) -> None:  # noqa: ANN001
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
