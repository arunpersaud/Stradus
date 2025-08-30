"""Tests for parser module."""

import pytest
from vortran.parser import parse_output, verify_result


class TestParseOutput:
    """Tests for parse_output function."""

    def test_parse_output_valid_input(self):
        """Test parsing valid laser response."""
        input_str = "\nC=1\nLP=50.0\nLE=0\n"
        result = parse_output(input_str)
        # Note: parser excludes last line, so LE=0 is not included
        assert result == ["1", "50.0"]

    def test_parse_output_single_value(self):
        """Test parsing single value response."""
        input_str = "\nBPT=25.3\nEND\n"
        result = parse_output(input_str)
        # Parser excludes last line, so we need at least 2 lines after header
        assert result == ["25.3"]

    def test_parse_output_none_input(self):
        """Test parsing None input."""
        result = parse_output(None)
        assert result is None

    def test_parse_output_empty_string(self):
        """Test parsing empty string."""
        result = parse_output("")
        assert result == []

    def test_parse_output_only_newlines(self):
        """Test parsing string with only newlines."""
        # Empty lines cause IndexError when trying to split on "="
        with pytest.raises(IndexError):
            parse_output("\n\n\n")

    def test_parse_output_with_spaces(self):
        """Test parsing values with extra spaces."""
        input_str = "\nC = 1 \nLP= 50.0\nEND\n"
        result = parse_output(input_str)
        # Parser excludes last line, need END marker
        assert result == ["1", "50.0"]

    def test_parse_output_malformed_line(self):
        """Test parsing with malformed line (no equals sign)."""
        input_str = "\nC=1\nMALFORMED\nLP=50.0\nEND\n"
        # This will likely cause an IndexError - testing current behavior
        with pytest.raises(IndexError):
            parse_output(input_str)


class TestVerifyResult:
    """Tests for verify_result function."""

    def test_verify_result_single_command_present(self):
        """Test verification when single command is present."""
        input_str = "C=1\nLP=50.0\nLE=0"
        command = ["C"]
        assert verify_result(input_str, command) is True

    def test_verify_result_single_command_missing(self):
        """Test verification when single command is missing."""
        input_str = "LP=50.0\nLE=0"
        command = ["C"]
        assert verify_result(input_str, command) is False

    def test_verify_result_multiple_commands_all_present(self):
        """Test verification when all commands are present."""
        input_str = "C=1\nLP=50.0\nLE=0"
        command = ["C", "LP", "LE"]
        assert verify_result(input_str, command) is True

    def test_verify_result_multiple_commands_some_missing(self):
        """Test verification when some commands are missing."""
        input_str = "C=1\nLP=50.0"
        command = ["C", "LP", "LE"]
        assert verify_result(input_str, command) is False

    def test_verify_result_empty_command_list(self):
        """Test verification with empty command list."""
        input_str = "C=1\nLP=50.0"
        command = []
        assert verify_result(input_str, command) is True

    def test_verify_result_empty_input(self):
        """Test verification with empty input."""
        input_str = ""
        command = ["C"]
        assert verify_result(input_str, command) is False

    def test_verify_result_partial_command_match(self):
        """Test that partial matches DO count (current behavior)."""
        input_str = "LPS=100\nLC=2.5"  # Contains "LP" and "C" as substrings
        command = ["LP", "C"]
        # Current implementation uses 'in' operator, so substrings match
        assert verify_result(input_str, command) is True
