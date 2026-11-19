"""Unit tests for the CNJ case number helpers."""

import pytest

from purepii_br import is_valid_processo_cnj, mask_processo_cnj, unmask_processo_cnj


_INT_MODULUS = 97


def _dd(tuple_parts: tuple[str, str, str, str, str]) -> str:
    """Compute the check digits for (N, AAAA, J, TR, OOOO); generated numbers only."""
    int_base = int("".join(tuple_parts) + "00")
    return f"{98 - int_base % _INT_MODULUS:02d}"


def _make(tuple_parts: tuple[str, str, str, str, str], *, str_dd: str) -> str:
    """Build a bare 20-digit number from its parts and the given check digits."""
    str_n, str_aaaa, str_j, str_tr, str_oooo = tuple_parts
    return f"{str_n}{str_dd}{str_aaaa}{str_j}{str_tr}{str_oooo}"


def _shifted(str_dd: str) -> str:
    """Return a different DD, still inside 02..98."""
    return f"{(int(str_dd) - 1) % 97 + 2:02d}"


_LIST_TUPLES = [
    ("0000001", "2020", "8", "26", "0001"),
    ("1234567", "2023", "4", "03", "6000"),
    ("0012345", "2019", "5", "02", "0200"),
    ("9999999", "2008", "1", "00", "0000"),
    ("0000000", "2030", "9", "99", "9999"),
]


@pytest.mark.parametrize(
    "str_value",
    [
        "0000001-84.2020.8.26.0001",
        "1234567-73.2023.4.03.6000",
        "0012345-37.2019.5.02.0200",
        "00000018420208260001",
        "12345677320234036000",
    ],
)
def test_is_valid_processo_cnj_issue_valid_examples_return_true(str_value: str) -> None:
    """The issue's valid examples pass, masked and bare."""
    assert is_valid_processo_cnj(str_value) is True


@pytest.mark.parametrize(
    "str_value",
    [
        "0000001-85.2020.8.26.0001",
        "1234567-00.2023.4.03.6000",
        "0012345-37.2019.5.02.020",
        "",
    ],
)
def test_is_valid_processo_cnj_issue_invalid_examples_return_false(str_value: str) -> None:
    """The issue's invalid examples return False without raising."""
    assert is_valid_processo_cnj(str_value) is False


@pytest.mark.parametrize("str_dd", ["00", "01", "99"])
def test_is_valid_processo_cnj_dd_out_of_range_returns_false(str_dd: str) -> None:
    """DD outside 02..98 is rejected even if the modulus would match."""
    assert is_valid_processo_cnj(f"0000000{str_dd}20208260001") is False


@pytest.mark.parametrize("tuple_parts", _LIST_TUPLES)
def test_is_valid_processo_cnj_generated_dd_returns_true(
    tuple_parts: tuple[str, str, str, str, str],
) -> None:
    """A computed DD makes the number valid."""
    assert is_valid_processo_cnj(_make(tuple_parts, str_dd=_dd(tuple_parts))) is True


@pytest.mark.parametrize("tuple_parts", _LIST_TUPLES)
def test_is_valid_processo_cnj_generated_wrong_dd_returns_false(
    tuple_parts: tuple[str, str, str, str, str],
) -> None:
    """Any other DD makes the number invalid."""
    assert is_valid_processo_cnj(_make(tuple_parts, str_dd=_shifted(_dd(tuple_parts)))) is False


@pytest.mark.parametrize("int_pos", [7, 8])
def test_is_valid_processo_cnj_changed_dd_digit_returns_false(int_pos: int) -> None:
    """Changing either DD digit of a valid number invalidates it."""
    str_ok = "00000018420208260001"
    str_bad = str_ok[:int_pos] + str((int(str_ok[int_pos]) + 1) % 10) + str_ok[int_pos + 1 :]
    assert is_valid_processo_cnj(str_bad) is False


@pytest.mark.parametrize(
    "str_value",
    ["０００００１８４２０２０８２６０００１", "٠٠٠٠٠١٨٤٢٠٢٠٨٢٦٠٠٠١"],
)
def test_is_valid_processo_cnj_full_width_returns_false(str_value: str) -> None:
    """Full-width and Arabic-Indic digits are never accepted."""
    assert is_valid_processo_cnj(str_value) is False


def test_is_valid_processo_cnj_float_tail_returns_true() -> None:
    """A float-coerced bare number is accepted."""
    assert is_valid_processo_cnj("00000018420208260001.0") is True


def test_is_valid_processo_cnj_short_number_is_zero_padded() -> None:
    """Leading zeros lost by a numeric store are restored before checking."""
    assert is_valid_processo_cnj("18420208260001") is True


def test_unmask_processo_cnj_strips_punctuation() -> None:
    """Punctuation is removed."""
    assert unmask_processo_cnj("0000001-84.2020.8.26.0001") == "00000018420208260001"


def test_unmask_processo_cnj_float_tail_is_dropped() -> None:
    """A float ``.0`` tail is removed."""
    assert unmask_processo_cnj("12345677320234036000.0") == "12345677320234036000"


def test_unmask_processo_cnj_pads_zeros_to_20() -> None:
    """Short values are left-padded with zeros."""
    assert unmask_processo_cnj("18420208260001") == "00000018420208260001"


def test_unmask_processo_cnj_empty_returns_empty() -> None:
    """Empty input stays empty rather than becoming 20 zeros."""
    assert unmask_processo_cnj("") == ""


@pytest.mark.parametrize("str_value", ["０００1", "٠٠٠1"])
def test_unmask_processo_cnj_non_ascii_digits_are_dropped(str_value: str) -> None:
    """Full-width and Arabic-Indic digits are filtered out, not kept."""
    assert unmask_processo_cnj(str_value) == "00000000000000000001"


def test_mask_processo_cnj_twenty_digits_returns_masked() -> None:
    """A 20-digit value gets the CNJ mask."""
    assert mask_processo_cnj("00000018420208260001") == "0000001-84.2020.8.26.0001"


def test_mask_processo_cnj_masked_input_is_stable() -> None:
    """Masking an already masked value is a no-op."""
    assert mask_processo_cnj("0000001-84.2020.8.26.0001") == "0000001-84.2020.8.26.0001"


def test_mask_processo_cnj_nineteen_digits_returns_zero_padded_masked() -> None:
    """19 digits are padded to 20 first, as unmask does."""
    assert mask_processo_cnj("0000001842020826000") == "0000000-18.4202.0.82.6000"


def test_mask_processo_cnj_over_length_returns_unmasked() -> None:
    """More than 20 digits cannot be masked: the bare value comes back."""
    assert mask_processo_cnj("123456789012345678901") == "123456789012345678901"


def test_mask_processo_cnj_full_width_digits_never_pass_through() -> None:
    """Full-width digits are dropped, leaving nothing to mask."""
    assert mask_processo_cnj("１２３") == ""


def test_is_valid_processo_cnj_non_str_raises_type_error() -> None:
    """A non-str argument raises TypeError from the type checker."""
    with pytest.raises(TypeError):
        is_valid_processo_cnj(123)  # type: ignore[arg-type]
