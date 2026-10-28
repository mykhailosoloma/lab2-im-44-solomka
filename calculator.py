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
