import codecs
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

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


class InvalidKeyError(CalculatorError):
    pass


class InvalidSequenceError(CalculatorError):
    pass


class DivisionByZeroError(CalculatorError):
    pass


def parse(text):
    line = text.rstrip("\r\n")
    if not line:
        return []

    keys = line.split(" ")
    if "" in keys:
        raise ParseError("Key names must be separated by exactly one space")
    return keys


class KeyKind(Enum):
    DIGIT = "digit"
    OPERATION = "operation"
    EQUALS = "equals"


class Stage(Enum):
    START = "nothing has been typed yet"
    FIRST_NUMBER = "typing the first number"
    OPERATION = "an operation has just been selected"
    SECOND_NUMBER = "typing the second number"
    RESULT = "the result is already shown"


TRANSITIONS = {
    (Stage.START, KeyKind.DIGIT): Stage.FIRST_NUMBER,
    (Stage.FIRST_NUMBER, KeyKind.DIGIT): Stage.FIRST_NUMBER,
    (Stage.FIRST_NUMBER, KeyKind.OPERATION): Stage.OPERATION,
    (Stage.OPERATION, KeyKind.DIGIT): Stage.SECOND_NUMBER,
    (Stage.SECOND_NUMBER, KeyKind.DIGIT): Stage.SECOND_NUMBER,
    (Stage.SECOND_NUMBER, KeyKind.EQUALS): Stage.RESULT,
}


@dataclass
class CalculatorState:
    screen: int = 0
    first_number: int = 0
    op: str | None = None
    stage: Stage = Stage.START


def key_kind(key):
    if key in DIGITS:
        return KeyKind.DIGIT
    if key in OPERATIONS:
        return KeyKind.OPERATION
    if key == EQUALS:
        return KeyKind.EQUALS
    raise InvalidKeyError(f"Unknown key {key!r}")


def handle_key_press(state, key):
    kind = key_kind(key)
    next_stage = TRANSITIONS.get((state.stage, kind))
    if next_stage is None:
        raise InvalidSequenceError(f"Key {key!r} is not allowed when {state.stage.value}")

    if kind is KeyKind.DIGIT:
        if state.stage is Stage.OPERATION:
            state.screen = int(key)
        else:
            state.screen = state.screen * 10 + int(key)
    elif kind is KeyKind.OPERATION:
        state.first_number = state.screen
        state.op = key
    else:
        if state.op == "/" and state.screen == 0:
            raise DivisionByZeroError("Division by zero")
        state.screen = OPERATIONS[state.op](state.first_number, state.screen)
    state.stage = next_stage


def calculate(keys):
    state = CalculatorState()
    for key in keys:
        handle_key_press(state, key)
    return state.screen


def read_input(path):
    data = Path(path).read_bytes()
    if data.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        return data.decode("utf-16")
    return data.decode("utf-8-sig")


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) not in (1, 2):
        print("Usage: python calculator.py <input file> [<output file>]", file=sys.stderr)
        return 2

    try:
        result = calculate(parse(read_input(args[0])))
        output = f"{result}\n"
        if len(args) == 2:
            Path(args[1]).write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
    except (CalculatorError, OSError, UnicodeDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
