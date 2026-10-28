import pytest

from calculator import CalculatorState, handle_key_press

DIGITS = list("0123456789")
OPERATIONS = ["+", "-", "*", "/"]


def state_after(keys):
    state = CalculatorState()
    for key in keys.split():
        handle_key_press(state, key)
    return state


def test_screen_shows_zero_initially():
    assert CalculatorState().screen == 0


def test_no_operation_is_selected_initially():
    assert CalculatorState().op is None


@pytest.mark.parametrize("digit", DIGITS)
def test_first_digit_is_shown_on_screen(digit):
    state = CalculatorState()
    handle_key_press(state, digit)
    assert state.screen == int(digit)


@pytest.mark.parametrize("digit", DIGITS)
def test_next_digit_becomes_least_significant(digit):
    state = state_after("4 2")
    handle_key_press(state, digit)
    assert state.screen == 420 + int(digit)


def test_leading_zero_is_dropped():
    state = state_after("0")
    handle_key_press(state, "7")
    assert state.screen == 7


@pytest.mark.parametrize("op", OPERATIONS)
def test_operation_is_remembered(op):
    state = state_after("1 2 3")
    handle_key_press(state, op)
    assert state.op == op


@pytest.mark.parametrize("op", OPERATIONS)
def test_operation_saves_screen_as_first_number(op):
    state = state_after("1 2 3")
    handle_key_press(state, op)
    assert state.first_number == 123


@pytest.mark.parametrize("op", OPERATIONS)
def test_screen_still_shows_first_number_after_operation(op):
    state = state_after("1 2 3")
    handle_key_press(state, op)
    assert state.screen == 123


def test_first_digit_after_operation_replaces_screen():
    state = state_after("1 2 3 +")
    handle_key_press(state, "4")
    assert state.screen == 4


def test_zero_can_start_second_number():
    state = state_after("1 2 3 +")
    handle_key_press(state, "0")
    assert state.screen == 0


def test_next_digits_of_second_number_are_appended():
    state = state_after("1 2 3 + 4")
    handle_key_press(state, "5")
    assert state.screen == 45


def test_typing_second_number_keeps_first_number_and_operation():
    state = state_after("1 2 3 * 4 5")
    assert (state.first_number, state.op) == (123, "*")


@pytest.mark.parametrize(
    "keys, expected",
    [("7 + 3", 10), ("7 - 3", 4), ("7 * 3", 21), ("7 / 3", 2)],
    ids=["add", "subtract", "multiply", "divide"],
)
def test_equals_applies_operation_to_first_number_and_screen(keys, expected):
    state = state_after(keys)
    handle_key_press(state, "=")
    assert state.screen == expected


def test_subtraction_takes_second_number_from_first():
    state = state_after("3 - 7")
    handle_key_press(state, "=")
    assert state.screen == -4


def test_division_divides_first_number_by_second():
    state = state_after("2 / 8")
    handle_key_press(state, "=")
    assert state.screen == 0
