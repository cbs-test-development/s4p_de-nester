"""Tests for :mod:`app.denest.naming`."""

from __future__ import annotations

import pytest

from app.denest.naming import new_filename, safe_token, switch_gpu_token, unique_name


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Switch 2-1", "Switch_2-1"),
        ("  padded  ", "padded"),
        ('a<b>c:d"e/f\\g|h?i*j,k', "abcdefghijk"),
        ("control\tchars\nremoved", "controlcharsremoved"),
        ("many   spaces", "many_spaces"),
        ("a _ b", "a_b"),
        ("._edge._", "edge"),
        ("", "Unknown"),
        ("<>:", "Unknown"),
    ],
)
def test_safe_token(value: str, expected: str) -> None:
    assert safe_token(value) == expected


@pytest.mark.parametrize(
    ("array_location", "expected"),
    [
        ("Switch 2-1 GPU 10-16 9-16, GPU", "Switch_2-1_GPU_10-16_9-16"),
        ("Switch 1, GPU 3, GPU", "Switch_1_GPU_3"),
        ("Switch 1 GPU 3", "Switch_1_GPU_3"),
        (", GPU", "Unknown"),
    ],
)
def test_switch_gpu_token_drops_text_after_the_last_comma(
    array_location: str, expected: str
) -> None:
    assert switch_gpu_token(array_location) == expected


def test_new_filename_matches_the_documented_example() -> None:
    name = new_filename(
        "Switch 2-1 GPU 10-16 9-16, GPU", "1", "96637071293261032812672_739908p5304_PASS.s4p"
    )

    assert name == "Switch_2-1_GPU_10-16_9-16_Leg_1_96637071293261032812672_739908p5304_PASS.s4p"


def test_new_filename_keeps_an_uppercase_suffix() -> None:
    assert new_filename("Sw, GPU", "2", "x.S4P") == "Sw_Leg_2_x.S4P"


def test_new_filename_adds_a_missing_suffix() -> None:
    assert new_filename("Sw, GPU", "2", "x") == "Sw_Leg_2_x.s4p"


def test_new_filename_sanitises_the_leg_location() -> None:
    assert new_filename("Sw, GPU", " 3 / A ", "x.s4p") == "Sw_Leg_3_A_x.s4p"


def test_unique_name_returns_an_unused_name_unchanged() -> None:
    used: set[str] = set()

    assert unique_name("a.s4p", used) == "a.s4p"
    assert used == {"a.s4p"}


def test_unique_name_numbers_repeats_before_the_suffix() -> None:
    used: set[str] = set()

    names = [unique_name("a.s4p", used) for _ in range(3)]

    assert names == ["a.s4p", "a_2.s4p", "a_3.s4p"]


def test_unique_name_treats_names_differing_only_in_case_as_clashes() -> None:
    used: set[str] = set()
    unique_name("A.s4p", used)

    assert unique_name("a.S4P", used) == "a_2.S4P"


def test_unique_name_without_a_suffix_appends_the_number() -> None:
    used: set[str] = set()
    unique_name("a", used)

    assert unique_name("a", used) == "a_2"


def test_unique_name_skips_numbers_already_taken() -> None:
    used = {"a.s4p", "a_2.s4p"}

    assert unique_name("a.s4p", used) == "a_3.s4p"
