import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from calculator import main

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def input_file(tmp_path):
    def write(text, encoding="utf-8"):
        path = tmp_path / "input.txt"
        path.write_text(text, encoding=encoding)
        return path
    return write


@pytest.fixture
def output_path(tmp_path):
    return tmp_path / "output.txt"


def test_result_is_written_to_output_file(input_file, output_path):
    assert main([str(input_file("1 2 3 + 4 5 6 =\n")), str(output_path)]) == 0
    assert output_path.read_text(encoding="utf-8") == "579\n"


def test_negative_result_is_written_with_minus_sign(input_file, output_path):
    main([str(input_file("1 0 - 1 0 0 =")), str(output_path)])
    assert output_path.read_text(encoding="utf-8") == "-90\n"


def test_empty_input_file_gives_zero(input_file, output_path):
    main([str(input_file("")), str(output_path)])
    assert output_path.read_text(encoding="utf-8") == "0\n"


@pytest.mark.parametrize(
    "encoding",
    [
        pytest.param("utf-8-sig", id="utf-8-with-bom"),
        pytest.param("utf-16", id="utf-16-with-bom"),
    ],
)
def test_input_file_in_windows_encodings_is_accepted(input_file, output_path, encoding):
    main([str(input_file("7 * 6 =", encoding)), str(output_path)])
    assert output_path.read_text(encoding="utf-8") == "42\n"


def test_result_is_printed_when_output_file_is_not_given(input_file, capsys):
    assert main([str(input_file("1 2 3 + 4 5 6 ="))]) == 0
    assert capsys.readouterr().out == "579\n"


@pytest.mark.parametrize(
    "text, message",
    [
        pytest.param("5 + + 3 =", "not allowed", id="forbidden-sequence"),
        pytest.param("5 / 0 =", "Division by zero", id="division-by-zero"),
        pytest.param("1 a", "Unknown key", id="unknown-key"),
        pytest.param("1  2", "exactly one space", id="bad-separator"),
    ],
)
def test_invalid_input_is_reported_and_no_output_is_written(
    input_file, output_path, capsys, text, message
):
    assert main([str(input_file(text)), str(output_path)]) == 1
    assert message in capsys.readouterr().err
    assert not output_path.exists()


def test_input_file_that_is_not_text_is_reported(tmp_path, output_path, capsys):
    input_path = tmp_path / "input.txt"
    input_path.write_bytes(b"1 + \xff\xfe\xfd =")
    assert main([str(input_path), str(output_path)]) == 1
    assert "Error" in capsys.readouterr().err
    assert not output_path.exists()


def test_missing_input_file_is_reported(tmp_path, capsys):
    assert main([str(tmp_path / "missing.txt")]) == 1
    assert "missing.txt" in capsys.readouterr().err


def test_unwritable_output_path_is_reported(input_file, tmp_path, capsys):
    output_in_missing_dir = tmp_path / "no-such-dir" / "output.txt"
    assert main([str(input_file("1 + 2 =")), str(output_in_missing_dir)]) == 1
    assert "Error" in capsys.readouterr().err


@pytest.mark.parametrize("args", [[], ["a", "b", "c"]], ids=["no-arguments", "too-many"])
def test_wrong_number_of_arguments_prints_usage(args, capsys):
    assert main(args) == 2
    assert "Usage" in capsys.readouterr().err


def test_script_computes_example_from_examples_folder(output_path):
    completed = subprocess.run(
        [sys.executable, "calculator.py", "examples/input.txt", str(output_path)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    expected = (PROJECT_ROOT / "examples" / "expected_output.txt").read_text(encoding="utf-8")
    assert output_path.read_text(encoding="utf-8") == expected


def test_script_exit_code_is_nonzero_on_error(input_file, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["calculator.py", str(input_file("5 / 0 ="))])
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(str(PROJECT_ROOT / "calculator.py"), run_name="__main__")
    assert exit_info.value.code == 1
