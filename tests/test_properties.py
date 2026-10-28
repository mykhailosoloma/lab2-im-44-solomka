import re

from hypothesis import given
from hypothesis import strategies as st

from calculator import DivisionByZeroError, InvalidSequenceError, calculate

numbers = st.integers(min_value=0, max_value=10**30)
positive_numbers = st.integers(min_value=1, max_value=10**30)
operations = st.sampled_from(["+", "-", "*", "/"])
any_key = st.sampled_from(list("0123456789+-*/="))

ALLOWED_ORDER = re.compile(r"\d*|\d+[-+*/]\d*|\d+[-+*/]\d+=")


def typed(number):
    return list(str(number))


def expression(a, op, b):
    return typed(a) + [op] + typed(b) + ["="]


@given(numbers)
def test_typed_number_is_shown_on_screen(n):
    assert calculate(typed(n)) == n


@given(st.integers(min_value=1, max_value=20), numbers)
def test_leading_zeros_do_not_change_number(zeros, n):
    assert calculate(["0"] * zeros + typed(n)) == n


@given(numbers, operations)
def test_first_number_stays_on_screen_after_operation(a, op):
    assert calculate(typed(a) + [op]) == a


@given(numbers, operations, numbers)
def test_second_number_is_on_screen_until_equals(a, op, b):
    assert calculate(typed(a) + [op] + typed(b)) == b


@given(numbers, numbers)
def test_addition_matches_integer_arithmetic(a, b):
    assert calculate(expression(a, "+", b)) == a + b


@given(numbers, numbers)
def test_subtraction_matches_integer_arithmetic(a, b):
    assert calculate(expression(a, "-", b)) == a - b


@given(numbers, numbers)
def test_multiplication_matches_integer_arithmetic(a, b):
    assert calculate(expression(a, "*", b)) == a * b


@given(numbers, positive_numbers)
def test_division_rounds_down(a, b):
    quotient = calculate(expression(a, "/", b))
    assert b * quotient <= a < b * (quotient + 1)


@given(st.lists(any_key, max_size=12))
def test_key_sequence_is_accepted_only_in_allowed_order(keys):
    allowed = ALLOWED_ORDER.fullmatch("".join(keys)) is not None
    try:
        calculate(keys)
    except InvalidSequenceError:
        assert not allowed
    except DivisionByZeroError:
        assert allowed
    else:
        assert allowed
