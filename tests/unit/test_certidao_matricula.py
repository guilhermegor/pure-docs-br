"""Unit tests for the certificate matrícula helpers."""

import pytest

from purepii_br import (
    certidao_matricula,
    is_valid_certidao_matricula,
    mask_certidao_matricula,
    unmask_certidao_matricula,
)
from purepii_br.certidao_matricula import (
    _TUPLE_WEIGHTS_DV1 as _W1,
    _TUPLE_WEIGHTS_DV2 as _W2,
    _compute_dvs,
    _luhn_ok,
    _weighted_dv,
)


STR_SOURCE: str = "10453901552013100012021000012321"

LIST_VALID: list[str] = [
    STR_SOURCE,
    "12345501552020100001005000000771",
    "27801001552024200110120000045607",
    "99999502552010400007003000099969",
    "55555701552018100099250000123409",
    "10453901551800100012021000012329",
    "10453901552013900012021000012398",
    "104539015520131000120210000123xx",
    "104539015520131000120210000123XX",
    "10453901552013100012021000000412",
    "10453901552013100012021000000821",
]

LIST_INVALID: list[str] = [
    "10453901552013100012021000012322",
    "10453901542013100012021000012322",
    "10453901552013000012021000012387",
    "1045390155201310001202100001232",
    "104539015520131000120210000123x",
    "10453801552013100012021000012369",
    "10453900552013100012021000012340",
    "10453901551799100012021000012388",
    "10453901551013100012021000012313",
    "00000000000000000000000000000000",
    "",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEF",
]


@pytest.mark.parametrize("str_value", LIST_VALID)
def test_is_valid_certidao_matricula_valid_returns_true(str_value: str) -> None:
    """Accept the source example, synthetic numbers and the ``xx`` DV."""
    assert is_valid_certidao_matricula(str_value) is True


@pytest.mark.parametrize("str_value", LIST_VALID)
def test_is_valid_certidao_matricula_masked_returns_true(str_value: str) -> None:
    """Accept the masked form."""
    assert is_valid_certidao_matricula(mask_certidao_matricula(str_value)) is True


@pytest.mark.parametrize("str_value", LIST_INVALID)
def test_is_valid_certidao_matricula_invalid_returns_false(str_value: str) -> None:
    """Reject wrong DVs, fields out of range, bad CNS, bad lengths and junk."""
    assert is_valid_certidao_matricula(str_value) is False


def test_is_valid_certidao_matricula_future_year_returns_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With the clock fixed at 2026, year 2099 is in the future."""
    monkeypatch.setattr(certidao_matricula, "_current_year", lambda: 2026)
    assert is_valid_certidao_matricula("10453901552099100012021000012365") is False


def test_is_valid_certidao_matricula_year_reached_returns_true(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With the clock fixed at 2099, the same value is accepted."""
    monkeypatch.setattr(certidao_matricula, "_current_year", lambda: 2099)
    assert is_valid_certidao_matricula("10453901552099100012021000012365") is True


def test_is_valid_certidao_matricula_masked_xx_returns_true() -> None:
    """Accept a literal masked value ending in ``-XX``."""
    assert is_valid_certidao_matricula("104539 01 55 2013 1 00012 021 0000123-XX") is True


def test_is_valid_certidao_matricula_extra_x_returns_false() -> None:
    """A stray ``X`` is not silently dropped."""
    assert is_valid_certidao_matricula(f"{STR_SOURCE}X") is False


def test_is_valid_certidao_matricula_dotted_dv_zero_pair_returns_true() -> None:
    """``.00`` after 30 digits is the DV pair, not a float tail."""
    assert is_valid_certidao_matricula("104539015520131000120210000513.00") is True


def test_is_valid_certidao_matricula_masked_float_tail_returns_true() -> None:
    """A float tail after the masked form is dropped."""
    assert is_valid_certidao_matricula("104539 01 55 2013 1 00012 021 0000123-21.0") is True


def test_unmask_certidao_matricula_extra_x_returns_empty() -> None:
    """A stray ``X`` yields an empty string."""
    assert unmask_certidao_matricula(f"{STR_SOURCE}X") == ""


def test_unmask_certidao_matricula_overlength_is_not_truncated() -> None:
    """Longer input keeps every digit."""
    assert unmask_certidao_matricula("1" * 32 + "-1") == "1" * 33


def test_mask_certidao_matricula_xx_keeps_dv() -> None:
    """The ``XX`` DV is masked like digits."""
    assert mask_certidao_matricula("104539015520131000120210000123xx").endswith("0000123-XX")


def test_is_valid_certidao_matricula_non_str_raises_type_error() -> None:
    """A non-str input is a caller bug the runtime type checker rejects."""
    with pytest.raises(TypeError):
        is_valid_certidao_matricula(10453901552013100012021000012321)  # type: ignore[arg-type]


def test_weighted_dv_source_dv1_sum_288_is_2() -> None:
    """The source example sums to 288, remainder 2."""
    assert _weighted_dv("104539015520131000120210000123", tuple_weights=_W1) == 2


def test_weighted_dv_source_dv2_sum_309_is_1() -> None:
    """The source example sums to 309, remainder 1."""
    assert _weighted_dv("1045390155201310001202100001232", tuple_weights=_W2) == 1


def test_compute_dvs_dv1_remainder_ten_becomes_one() -> None:
    """Payload ...0004 gives remainder 10 on DV1, read as 1."""
    assert _compute_dvs("104539015520131000120210000004") == "12"


def test_compute_dvs_dv2_remainder_ten_becomes_one() -> None:
    """Payload ...0008 gives remainder 10 on DV2, read as 1."""
    assert _compute_dvs("104539015520131000120210000008") == "21"


def test_luhn_ok_valid_cns_returns_true() -> None:
    """``104539`` ends in the Luhn check digit of ``10453``."""
    assert _luhn_ok("104539") is True


def test_luhn_ok_wrong_digit_returns_false() -> None:
    """``104538`` has the wrong check digit."""
    assert _luhn_ok("104538") is False


def test_unmask_certidao_matricula_float_tail_is_stripped() -> None:
    """A float ``.0`` tail is dropped."""
    assert unmask_certidao_matricula(f"{STR_SOURCE}.0") == STR_SOURCE


def test_unmask_certidao_matricula_masked_returns_digits() -> None:
    """Spaces and the hyphen are stripped."""
    assert unmask_certidao_matricula("104539 01 55 2013 1 00012 021 0000123-21") == STR_SOURCE


def test_unmask_certidao_matricula_short_digits_are_zero_padded() -> None:
    """Digits-only input is left-padded to 32."""
    assert unmask_certidao_matricula("123") == "0" * 29 + "123"


def test_unmask_certidao_matricula_xx_dv_is_kept_upper() -> None:
    """The ``xx`` DV survives, upper-cased."""
    assert unmask_certidao_matricula("104539015520131000120210000123xx").endswith("XX")


def test_unmask_certidao_matricula_empty_returns_empty() -> None:
    """Input with no digits yields an empty string."""
    assert unmask_certidao_matricula("abc") == ""


def test_mask_certidao_matricula_groups_with_spaces() -> None:
    """The mask is spaces, with a hyphen before the DV."""
    assert mask_certidao_matricula(STR_SOURCE) == "104539 01 55 2013 1 00012 021 0000123-21"


def test_mask_certidao_matricula_too_long_returns_unmasked() -> None:
    """A value that does not fit 32 comes back unmasked."""
    assert mask_certidao_matricula("1" * 32 + "-1") == "1" * 33
