from dataclasses import dataclass

DIGITS = frozenset("0123456789")
EQUALS = "="
OPERATIONS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a // b,
}


class CalculatorError(ValueError):
    pass


class ParseError(CalculatorError):
    pass


def parse(text):
    line = text.rstrip("\r\n")
    if not line:
        return []

    keys = line.split(" ")
    if "" in keys:
        raise ParseError("Key names must be separated by exactly one space")
    return keys


@dataclass
class CalculatorState:
    screen: int = 0
    first_number: int = 0
    op: str | None = None
    start_second_number: bool = False


def handle_key_press(state, key):
    if key in DIGITS:
        if state.start_second_number:
            state.screen = int(key)
            state.start_second_number = False
        else:
            state.screen = state.screen * 10 + int(key)
    elif key in OPERATIONS:
        state.first_number = state.screen
        state.op = key
        state.start_second_number = True
    elif key == EQUALS:
        state.screen = OPERATIONS[state.op](state.first_number, state.screen)


def calculate(keys):
    state = CalculatorState()
    for key in keys:
        handle_key_press(state, key)
    return state.screen
