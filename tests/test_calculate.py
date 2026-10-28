import pytest

from calculator import calculate, parse


def calc(text):
    return calculate(parse(text))


@pytest.mark.parametrize(
    "text, expected",
    [
        pytest.param("", 0, id="zero-initially"),
        pytest.param("5", 5, id="single-digit"),
        pytest.param("1 2", 12, id="digits-are-appended"),
        pytest.param("1 2 3 + 4 5 6 =", 579, id="addition"),
        pytest.param("1 2 3 - 2 3 =", 100, id="subtraction"),
        pytest.param("1 0 - 1 0 0 =", -90, id="negative-result"),
        pytest.param("1 0 * 2 2 =", 220, id="multiplication"),
        pytest.param("1 0 0 / 3 =", 33, id="integer-division"),
        pytest.param("9 / 1 0 =", 0, id="division-rounds-down"),
        pytest.param("1 2 3 +", 123, id="first-operand-shown-after-operation"),
        pytest.param("1 2 3 + 4", 4, id="second-operand-shown"),
        pytest.param("1 2 3 + 4 5 6", 456, id="second-operand-shown-before-equals"),
    ],
)
def test_examples_from_task(text, expected):
    assert calc(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        pytest.param("0", 0, id="single-zero"),
        pytest.param("0 0 7", 7, id="leading-zeros"),
        pytest.param("5 0 0", 500, id="trailing-zeros"),
        pytest.param("1 2 3 4 5 6 7 8 9 0", 1234567890, id="all-digits"),
    ],
)
def test_number_entry(text, expected):
    assert calc(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        pytest.param("0 + 0 =", 0, id="zero-plus-zero"),
        pytest.param("5 + 0 =", 5, id="plus-zero"),
        pytest.param("0 0 7 + 0 0 3 =", 10, id="leading-zeros-in-both-operands"),
        pytest.param("5 - 5 =", 0, id="equal-operands-difference"),
        pytest.param("0 - 5 =", -5, id="zero-minus-number"),
        pytest.param("7 * 0 =", 0, id="multiply-by-zero"),
        pytest.param("0 * 7 =", 0, id="zero-times-number"),
        pytest.param("7 * 1 =", 7, id="multiply-by-one"),
        pytest.param("6 / 3 =", 2, id="exact-division"),
        pytest.param("7 / 7 =", 1, id="divide-by-itself"),
        pytest.param("7 / 1 =", 7, id="divide-by-one"),
        pytest.param("0 / 7 =", 0, id="zero-divided-by-number"),
        pytest.param("1 / 1 0 0 0 =", 0, id="small-divided-by-large"),
        pytest.param("1 9 / 1 0 =", 1, id="1.9-rounds-down-to-1"),
        pytest.param("9 9 / 1 0 =", 9, id="9.9-rounds-down-not-up"),
    ],
)
def test_arithmetic_edge_cases(text, expected):
    assert calc(text) == expected


def test_large_numbers_are_exact_integers():
    assert calc("9 0 0 7 1 9 9 2 5 4 7 4 0 9 9 3 + 0 =") == 9007199254740993


def test_product_of_large_numbers_is_exact():
    assert calc("9 9 9 9 9 9 9 9 9 9 * 9 9 9 9 9 9 9 9 9 9 =") == 99999999980000000001


@pytest.mark.parametrize(
    "text",
    ["", "5", "1 2 3 +", "2 + 2 =", "2 - 3 =", "2 * 2 =", "6 / 3 =", "1 0 0 / 3 ="],
)
def test_result_is_int_not_float(text):
    assert type(calc(text)) is int


def test_calculate_accepts_list_of_key_names():
    assert calculate(["1", "+", "2", "="]) == 3


def test_calculate_of_no_keys_is_zero():
    assert calculate([]) == 0


def test_each_calculation_starts_with_fresh_state():
    calc("1 2")
    assert calc("3") == 3
