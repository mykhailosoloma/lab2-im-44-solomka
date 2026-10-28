import pytest

from calculator import ParseError, parse


def test_empty_input_has_no_keys():
    assert parse("") == []


def test_single_key():
    assert parse("5") == ["5"]


def test_keys_are_split_by_single_space():
    assert parse("1 2 3 + 4 5 6 =") == ["1", "2", "3", "+", "4", "5", "6", "="]


def test_parse_does_not_split_multi_character_tokens():
    assert parse("12 + 3") == ["12", "+", "3"]


@pytest.mark.parametrize(
    "text",
    ["1 + 2 =\n", "1 + 2 =\r\n", "1 + 2 =\n\n"],
    ids=["lf", "crlf", "blank-line-after"],
)
def test_trailing_line_break_is_ignored(text):
    assert parse(text) == ["1", "+", "2", "="]


@pytest.mark.parametrize("text", ["\n", "\r\n"], ids=["lf", "crlf"])
def test_file_with_only_line_break_has_no_keys(text):
    assert parse(text) == []


@pytest.mark.parametrize(
    "text",
    ["1  2", " 1 2", "1 2 ", " "],
    ids=["double-space", "leading-space", "trailing-space", "only-space"],
)
def test_keys_must_be_separated_by_exactly_one_space(text):
    with pytest.raises(ParseError):
        parse(text)
