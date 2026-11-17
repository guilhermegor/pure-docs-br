"""Unit tests for the state registration (Inscricao Estadual) helpers of the 27 UFs."""

import pytest

from pure_docs_br import (
    is_valid_inscricao_estadual,
    mask_inscricao_estadual,
    unmask_inscricao_estadual,
)
from pure_docs_br.inscricao_estadual import _DICT_MASKS, _DICT_VALIDATORS


_DICT_VALID: dict[str, tuple[str, str, str]] = {
    "AC": ("0100482300112", "0112345670027", "0198765430000"),
    "AL": ("240000048", "240123450", "243000014"),
    "AP": ("030123459", "030170011", "030200008"),
    "AM": ("041234561", "049999907", "031112226"),
    "BA": ("12345663", "61234557", "100000306"),
    "CE": ("060000015", "061234567", "070000115"),
    "DF": ("0730000100109", "0730000100281", "0712345670068"),
    "ES": ("999999990", "123456789", "990000125"),
    "GO": ("109876547", "101031106", "110000005"),
    "MA": ("120000385", "121234568", "129999997"),
    "MT": ("00130000019", "00130000027", "00012345679"),
    "MS": ("281234566", "500001235", "280000014"),
    "MG": ("0623079040081", "1234567890098", "3100000100048"),
    "PA": ("159999995", "750000023", "756543215"),
    "PB": ("060000015", "061234567", "123456789"),
    "PR": ("1234567850", "9000001209", "3000002070"),
    "PE": ("032141840", "18100100000049", "123456797"),
    "PI": ("012345679", "012345687", "190000147"),
    "RJ": ("12345674", "20000015", "99999993"),
    "RN": ("200400401", "2000400400", "201234564"),
    "RS": ("2243658792", "2243658806", "0190000112"),
    "RO": ("101625213", "00000000625213", "00000123456789"),
    "RR": ("240061536", "240066281", "240017556"),
    "SC": ("251040852", "252000005", "290000114"),
    "SE": ("271234563", "271234571", "270000119"),
    "SP": ("110042490114", "100000001007", "123456785016"),
    "TO": ("29010227836", "29010227844", "15030000014"),
}

_LIST_VALID: list[tuple[str, str]] = [
    (str_uf, str_ie) for str_uf, tuple_ies in _DICT_VALID.items() for str_ie in tuple_ies
]
_LIST_INVALID: list[tuple[str, str]] = [
    (str_uf, str_bad)
    for str_uf, tuple_ies in _DICT_VALID.items()
    for str_bad in (
        tuple_ies[0][:-1] + str((int(tuple_ies[0][-1]) + 1) % 10),
        tuple_ies[0][:-1],
        tuple_ies[0] + "00",
    )
]
_LIST_MASKED: list[tuple[str, str, str]] = [
    ("AC", "0100482300112", "01.004.823/001-12"),
    ("AL", "240000048", "24.000.004-8"),
    ("AP", "030123459", "03.012.345-9"),
    ("AM", "041234561", "04.123.456-1"),
    ("BA", "12345663", "123456-63"),
    ("BA", "100000306", "1000003-06"),
    ("CE", "060000015", "06000001-5"),
    ("DF", "0730000100109", "073.00001.001-09"),
    ("ES", "999999990", "99999999-0"),
    ("GO", "109876547", "10.987.654-7"),
    ("MA", "120000385", "12.000.038-5"),
    ("MT", "00130000019", "0013000001-9"),
    ("MS", "281234566", "28.123.456-6"),
    ("MG", "0623079040081", "062.307.904/0081"),
    ("PA", "159999995", "15-999999-5"),
    ("PB", "060000015", "06000001-5"),
    ("PR", "1234567850", "123.45678-50"),
    ("PE", "032141840", "0321418-40"),
    ("PE", "18100100000049", "18.1.001.0000004-9"),
    ("PI", "012345679", "01234567-9"),
    ("RJ", "12345674", "12.345.67-4"),
    ("RN", "200400401", "20.040.040-1"),
    ("RN", "2000400400", "20.0.040.040-0"),
    ("RS", "2243658792", "224/3658792"),
    ("RO", "101625213", "101.62521-3"),
    ("RO", "00000000625213", "0000000062521-3"),
    ("RR", "240061536", "24.006.153-6"),
    ("SC", "251040852", "251.040.852"),
    ("SE", "271234563", "27123456-3"),
    ("SP", "110042490114", "110.042.490.114"),
    ("TO", "29010227836", "29.01.022783-6"),
]


def test_dispatch_table_covers_the_27_ufs() -> None:
    """The validator table is the one declaration of the supported UFs."""
    assert len(_DICT_VALIDATORS) == 27


def test_mask_table_keys_are_the_validator_keys() -> None:
    """Every UF has a mask table and no mask exists for an unsupported UF."""
    assert set(_DICT_MASKS) == set(_DICT_VALIDATORS)


@pytest.mark.parametrize(("str_uf", "str_ie"), _LIST_VALID)
def test_is_valid_inscricao_estadual_valid_examples_return_true(
    *, str_uf: str, str_ie: str
) -> None:
    """Three valid values per UF, official examples first, pass."""
    assert is_valid_inscricao_estadual(str_ie, str_uf=str_uf) is True


@pytest.mark.parametrize(("str_uf", "str_ie"), _LIST_INVALID)
def test_is_valid_inscricao_estadual_invalid_examples_return_false(
    *, str_uf: str, str_ie: str
) -> None:
    """Wrong check digit, one digit short and two digits long are rejected per UF."""
    assert is_valid_inscricao_estadual(str_ie, str_uf=str_uf) is False


@pytest.mark.parametrize(
    "str_ie", ["110042490115", "110042491114", "11004249011", "", "1100424901140"]
)
def test_is_valid_inscricao_estadual_sp_issue_invalid_examples_return_false(str_ie: str) -> None:
    """The SP invalid examples of the issue return False without raising."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="SP") is False


@pytest.mark.parametrize("str_ie", ["110.042.490.114", "110042490114.0", " 110042490114 "])
def test_is_valid_inscricao_estadual_sp_any_shape_returns_true(str_ie: str) -> None:
    """The official SP example passes masked, with a float tail and with spaces."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="SP") is True


@pytest.mark.parametrize("str_ie", ["ISENTO", "isento", "P-011004249.0/002", "P011004249002"])
def test_is_valid_inscricao_estadual_letters_return_false(str_ie: str) -> None:
    """ISENTO and the SP producer-rural form (a letter) are not validated."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="SP") is False


@pytest.mark.parametrize("str_uf", ["XX", "sp", "", "SPP", "BR"])
def test_is_valid_inscricao_estadual_unknown_uf_returns_false(str_uf: str) -> None:
    """An unknown UF never raises: every IE is simply invalid."""
    assert is_valid_inscricao_estadual("110042490114", str_uf=str_uf) is False


def test_is_valid_inscricao_estadual_non_str_raises_type_error() -> None:
    """A non-str value is refused by the runtime type checker."""
    with pytest.raises(TypeError):
        is_valid_inscricao_estadual(110042490114, str_uf="SP")  # type: ignore[arg-type]


def test_is_valid_inscricao_estadual_str_uf_is_keyword_only() -> None:
    """The UF cannot be passed positionally."""
    with pytest.raises(TypeError):
        is_valid_inscricao_estadual("110042490114", "SP")  # type: ignore[misc]


def test_is_valid_inscricao_estadual_wrong_uf_returns_false() -> None:
    """The same digits are judged by the rule of the UF given."""
    assert is_valid_inscricao_estadual("110042490114", str_uf="MG") is False


@pytest.mark.parametrize("str_ie", ["030000020", "030170071", "030190290"])
def test_is_valid_inscricao_estadual_ap_ranges_return_true(str_ie: str) -> None:
    """AP rest 0 gives d=0 in the first and third range and d=1 in the second."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="AP") is True


@pytest.mark.parametrize("str_ie", ["030000021", "030170070", "030190291"])
def test_is_valid_inscricao_estadual_ap_ranges_swapped_d_return_false(str_ie: str) -> None:
    """The d constant of another range is rejected."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="AP") is False


@pytest.mark.parametrize("str_ie", ["101031051", "101100061", "101199971", "102000000"])
def test_is_valid_inscricao_estadual_go_rest_one_band_returns_true(str_ie: str) -> None:
    """GO: rest 1 gives 1 inside 10103105-10119997 and 0 outside."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="GO") is True


@pytest.mark.parametrize("str_ie", ["101031050", "101199970", "101200031", "102000001"])
def test_is_valid_inscricao_estadual_go_rest_one_band_swapped_returns_false(str_ie: str) -> None:
    """GO: the digit of the other side of the band is rejected."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="GO") is False


@pytest.mark.parametrize(("str_ie", "bool_expected"), [("110944020", True), ("110944021", True)])
def test_is_valid_inscricao_estadual_go_11094402_accepts_zero_and_one(
    *, str_ie: str, bool_expected: bool
) -> None:
    """GO: the registration 11094402 takes check digit 0 or 1."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="GO") is bool_expected


def test_is_valid_inscricao_estadual_go_11094402_rejects_two() -> None:
    """GO: the 11094402 exception stops at 0 and 1."""
    assert is_valid_inscricao_estadual("110944022", str_uf="GO") is False


@pytest.mark.parametrize("str_ie", ["300000015", "180000011", "000000000"])
def test_is_valid_inscricao_estadual_go_bad_prefix_returns_false(str_ie: str) -> None:
    """GO accepts only the prefixes 10, 11, 15 and 20 to 29."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="GO") is False


@pytest.mark.parametrize("str_ie", ["010048230011", "02" + "0048230011" + "2"])
def test_is_valid_inscricao_estadual_ac_wrong_length_returns_false(str_ie: str) -> None:
    """AC needs 13 digits."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="AC") is False


def test_is_valid_inscricao_estadual_ac_prefix_not_01_returns_false() -> None:
    """AC registrations start with 01."""
    assert is_valid_inscricao_estadual("0200482300112", str_uf="AC") is False


def test_is_valid_inscricao_estadual_df_prefix_not_07_returns_false() -> None:
    """DF registrations start with 07."""
    assert is_valid_inscricao_estadual("0830000100109", str_uf="DF") is False


@pytest.mark.parametrize("str_ie", ["29020227836", "29030227836", "29990227836"])
def test_is_valid_inscricao_estadual_to_type_codes_do_not_enter_the_sum(str_ie: str) -> None:
    """TO: positions 3 and 4 (01, 02, 03 or 99) are not part of the calculation."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="TO") is True


@pytest.mark.parametrize("str_ie", ["29050227836", "29000227836"])
def test_is_valid_inscricao_estadual_to_unknown_type_code_returns_false(str_ie: str) -> None:
    """TO: a type code outside 01, 02, 03 and 99 is rejected."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="TO") is False


@pytest.mark.parametrize("str_ie", ["240000048", "243000014", "248000772"])
def test_is_valid_inscricao_estadual_al_type_digits_return_true(str_ie: str) -> None:
    """AL: the type digit 0, 3 and 8 are accepted."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="AL") is True


def test_is_valid_inscricao_estadual_al_unknown_type_digit_returns_false() -> None:
    """AL: the type digit 4 is not one of 0, 3, 5, 7 and 8."""
    assert is_valid_inscricao_estadual("244000010", str_uf="AL") is False


@pytest.mark.parametrize("str_ie", ["15999999", "5999999", "169999995", "759999995"])
def test_is_valid_inscricao_estadual_pa_bad_prefix_or_length_returns_false(str_ie: str) -> None:
    """PA: prefixes 15 and 75-79 and exactly 9 digits."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="PA") is False


@pytest.mark.parametrize("str_ie", ["272000010", "292000010"])
def test_is_valid_inscricao_estadual_ms_prefix_not_28_or_50_returns_false(str_ie: str) -> None:
    """MS registrations start with 28 or 50."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="MS") is False


@pytest.mark.parametrize("str_ie", ["130000385", "220000385"])
def test_is_valid_inscricao_estadual_ma_prefix_not_12_returns_false(str_ie: str) -> None:
    """MA registrations start with 12."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="MA") is False


@pytest.mark.parametrize("str_ie", ["230000048", "340000048"])
def test_is_valid_inscricao_estadual_al_prefix_not_24_returns_false(str_ie: str) -> None:
    """AL registrations start with 24."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="AL") is False


@pytest.mark.parametrize("str_ie", ["220000000", "21000555"])
def test_is_valid_inscricao_estadual_rn_prefix_not_20_returns_false(str_ie: str) -> None:
    """RN registrations start with 20."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="RN") is False


@pytest.mark.parametrize("str_ie", ["230061536", "340061536"])
def test_is_valid_inscricao_estadual_rr_prefix_not_24_returns_false(str_ie: str) -> None:
    """RR registrations start with 24."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="RR") is False


@pytest.mark.parametrize("str_ie", ["040000000", "030000000"])
def test_is_valid_inscricao_estadual_ap_prefix_not_03_returns_false(str_ie: str) -> None:
    """AP registrations start with 03."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="AP") is False


@pytest.mark.parametrize(
    ("str_value", "str_expected"),
    [
        ("110.042.490.114", "110042490114"),
        ("110042490114.0", "110042490114"),
        ("110.042.490.114.0", "1100424901140"),
        ("0100482300112", "0100482300112"),
        ("", ""),
    ],
)
def test_unmask_inscricao_estadual_returns_digits_only(
    *, str_value: str, str_expected: str
) -> None:
    """Punctuation goes; the float tail goes only from an all-digit value; no padding."""
    assert unmask_inscricao_estadual(str_value) == str_expected


def test_unmask_inscricao_estadual_drops_non_ascii_digits() -> None:
    """Fullwidth digits are not ASCII digits and are removed."""
    assert unmask_inscricao_estadual("１１０042490114") == "042490114"


def test_unmask_inscricao_estadual_does_not_pad() -> None:
    """A lost leading zero stays lost."""
    assert unmask_inscricao_estadual("1.234.567") == "1234567"


@pytest.mark.parametrize(("str_uf", "str_ie", "str_masked"), _LIST_MASKED)
def test_mask_inscricao_estadual_formats_by_uf(
    *, str_uf: str, str_ie: str, str_masked: str
) -> None:
    """Each UF has its own mask, by digit count where it has more than one."""
    assert mask_inscricao_estadual(str_ie, str_uf=str_uf) == str_masked


def test_mask_inscricao_estadual_masked_input_is_unmasked_first() -> None:
    """An already masked value is masked again, not doubled."""
    assert mask_inscricao_estadual("110.042.490.114", str_uf="SP") == "110.042.490.114"


def test_mask_inscricao_estadual_wrong_length_returns_unmasked() -> None:
    """For 11 digits SP returns the bare value."""
    assert mask_inscricao_estadual("11004249011", str_uf="SP") == "11004249011"


def test_mask_inscricao_estadual_unknown_uf_returns_unmasked() -> None:
    """An unknown UF leaves the value unmasked."""
    assert mask_inscricao_estadual("110.042.490.114", str_uf="XX") == "110042490114"


def test_mask_inscricao_estadual_empty_returns_empty() -> None:
    """Empty input stays empty."""
    assert mask_inscricao_estadual("", str_uf="SP") == ""


def test_mask_inscricao_estadual_does_not_verify_check_digits() -> None:
    """Masking only formats: a wrong check digit is kept."""
    assert mask_inscricao_estadual("110042490115", str_uf="SP") == "110.042.490.115"


@pytest.mark.parametrize("str_ie", ["101625213", "00000000625213"])
def test_is_valid_inscricao_estadual_ro_old_and_new_formats_return_true(str_ie: str) -> None:
    """RO: the pre-2000 9-digit form and its zero-padded 14-digit form both pass."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="RO") is True


@pytest.mark.parametrize("str_ie", ["101625212", "00000000625212"])
def test_is_valid_inscricao_estadual_ro_wrong_dv_returns_false(str_ie: str) -> None:
    """RO: a wrong check digit fails in both formats."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="RO") is False


@pytest.mark.parametrize("str_ie", ["200400401", "2000400400"])
def test_is_valid_inscricao_estadual_rn_nine_and_ten_digits_return_true(str_ie: str) -> None:
    """RN: both the 9 and the 10 digit forms are valid."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="RN") is True


@pytest.mark.parametrize("str_ie", ["032141840", "18100100000049"])
def test_is_valid_inscricao_estadual_pe_new_and_old_formats_return_true(str_ie: str) -> None:
    """PE: the 9-digit e-Fisco and the 14-digit CACEPE forms are valid."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="PE") is True


@pytest.mark.parametrize("str_ie", ["12345663", "61234557", "100000306"])
def test_is_valid_inscricao_estadual_ba_modules_return_true(str_ie: str) -> None:
    """BA: mod 10 and mod 11 by the leading digit (8 digits) or the second digit (9)."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="BA") is True


@pytest.mark.parametrize("str_ie", ["12345636", "61234575", "100000360"])
def test_is_valid_inscricao_estadual_ba_swapped_dvs_return_false(str_ie: str) -> None:
    """BA: swapping the two check digits is detected."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="BA") is False


def test_is_valid_inscricao_estadual_short_ba_does_not_raise() -> None:
    """BA: a value shorter than the check digits is invalid, not an IndexError."""
    assert is_valid_inscricao_estadual("1", str_uf="BA") is False


@pytest.mark.parametrize("str_ie", ["062307904008", "0623079040082", "0623179040081"])
def test_is_valid_inscricao_estadual_mg_wrong_values_return_false(str_ie: str) -> None:
    """MG: a short value, a wrong DV2 and an altered city code are rejected."""
    assert is_valid_inscricao_estadual(str_ie, str_uf="MG") is False
