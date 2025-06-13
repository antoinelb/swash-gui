import io
import shutil
import sys
from unittest.mock import Mock, patch

import pytest
import tqdm

from src.utils import print as print_utils


class TestLoadPrint:
    def test_load_print_default_params(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test load_print with default parameters."""
        print_utils.load_print("Loading test")
        captured = capsys.readouterr()
        
        # Should include the bold symbol and text, padded to terminal width
        assert "[*]" in captured.out
        assert "Loading test" in captured.out
        assert captured.out.endswith("\r")

    def test_load_print_custom_symbol(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test load_print with custom symbol."""
        print_utils.load_print("Loading test", symbol="►")
        captured = capsys.readouterr()
        
        assert "[►]" in captured.out
        assert "Loading test" in captured.out

    def test_load_print_with_indent(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test load_print with indentation."""
        print_utils.load_print("Loading test", indent=4)
        captured = capsys.readouterr()
        
        # Should have 4 spaces of indentation after the \r
        assert captured.out.startswith("\r    ")
        assert "[*]" in captured.out
        assert "Loading test" in captured.out

    def test_load_print_custom_end(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test load_print with custom end character."""
        print_utils.load_print("Loading test", end="\n")
        captured = capsys.readouterr()
        
        assert "[*]" in captured.out
        assert "Loading test" in captured.out
        assert captured.out.endswith("\n")

    def test_load_print_echo_false(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test load_print with echo=False."""
        print_utils.load_print("Loading test", echo=False)
        captured = capsys.readouterr()
        
        # Should produce no output
        assert captured.out == ""

    @patch('shutil.get_terminal_size')
    def test_load_print_terminal_width_padding(
        self, 
        mock_terminal_size: Mock, 
        capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that load_print pads output to terminal width."""
        mock_terminal_size.return_value = Mock(columns=80)
        
        print_utils.load_print("Test")
        captured = capsys.readouterr()
        
        # The output should be padded to 80 characters (minus the \r and ANSI codes)
        # Just verify that ljust was called by checking the mock
        mock_terminal_size.assert_called()

    def test_load_print_ansi_formatting(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that load_print includes ANSI formatting codes."""
        print_utils.load_print("Test", symbol="X")
        captured = capsys.readouterr()
        
        # Should include bold formatting codes
        assert "\033[1m" in captured.out  # Bold start
        assert "\033[0m" in captured.out  # Reset


class TestDonePrint:
    def test_done_print_default_params(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test done_print with default parameters."""
        print_utils.done_print("Task completed")
        captured = capsys.readouterr()
        
        # Should include green colored symbol and text
        assert "[+]" in captured.out
        assert "Task completed" in captured.out
        assert captured.out.endswith("\n")

    def test_done_print_custom_symbol(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test done_print with custom symbol."""
        print_utils.done_print("Task completed", symbol="✓")
        captured = capsys.readouterr()
        
        assert "[✓]" in captured.out
        assert "Task completed" in captured.out

    def test_done_print_with_indent(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test done_print with indentation."""
        print_utils.done_print("Task completed", indent=2)
        captured = capsys.readouterr()
        
        # Should have 2 spaces of indentation after the \r
        assert captured.out.startswith("\r  ")
        assert "[+]" in captured.out
        assert "Task completed" in captured.out

    def test_done_print_echo_false(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test done_print with echo=False."""
        print_utils.done_print("Task completed", echo=False)
        captured = capsys.readouterr()
        
        # Should produce no output
        assert captured.out == ""

    @patch('src.utils.print.cursor_up')
    @patch('shutil.get_terminal_size')
    def test_done_print_overwrite_lines(
        self, 
        mock_terminal_size: Mock,
        mock_cursor_up: Mock,
        capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test done_print with overwrite_n_extra_lines."""
        mock_terminal_size.return_value = Mock(columns=80)
        
        print_utils.done_print("Task completed", overwrite_n_extra_lines=2)
        captured = capsys.readouterr()
        
        # cursor_up should be called twice: once to move up, once to position for final print
        assert mock_cursor_up.call_count == 2
        mock_cursor_up.assert_any_call(3)  # Move up 2 extra lines + 1
        
        # Should contain the task completion message
        assert "Task completed" in captured.out

    def test_done_print_ansi_formatting(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that done_print includes ANSI formatting codes."""
        print_utils.done_print("Test", symbol="X")
        captured = capsys.readouterr()
        
        # Should include bold and green formatting codes
        assert "\033[1m" in captured.out  # Bold start
        assert "\033[92m" in captured.out  # Green color
        assert "\033[0m" in captured.out  # Reset

    @patch('shutil.get_terminal_size')
    def test_done_print_terminal_width_padding(
        self, 
        mock_terminal_size: Mock, 
        capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that done_print pads output to terminal width."""
        mock_terminal_size.return_value = Mock(columns=80)
        
        print_utils.done_print("Test")
        captured = capsys.readouterr()
        
        # Just verify that terminal size was checked
        mock_terminal_size.assert_called()


class TestErrorPrint:
    def test_error_print_default_params(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test error_print with default parameters."""
        print_utils.error_print("Error occurred")
        captured = capsys.readouterr()
        
        # Should include red colored symbol and text
        assert "[!]" in captured.out
        assert "Error occurred" in captured.out

    def test_error_print_custom_symbol(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test error_print with custom symbol."""
        print_utils.error_print("Error occurred", symbol="✗")
        captured = capsys.readouterr()
        
        assert "[✗]" in captured.out
        assert "Error occurred" in captured.out

    def test_error_print_with_indent(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test error_print with indentation."""
        print_utils.error_print("Error occurred", indent=3)
        captured = capsys.readouterr()
        
        # Should have 3 spaces of indentation after the \r
        assert captured.out.startswith("\r   ")
        assert "[!]" in captured.out
        assert "Error occurred" in captured.out

    def test_error_print_echo_false(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test error_print with echo=False."""
        print_utils.error_print("Error occurred", echo=False)
        captured = capsys.readouterr()
        
        # Should produce no output
        assert captured.out == ""

    def test_error_print_ansi_formatting(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that error_print includes ANSI formatting codes."""
        print_utils.error_print("Test", symbol="X")
        captured = capsys.readouterr()
        
        # Should include bold and red formatting codes
        assert "\033[1m" in captured.out  # Bold start
        assert "\033[91m" in captured.out  # Red color
        assert "\033[0m" in captured.out  # Reset

    @patch('shutil.get_terminal_size')
    def test_error_print_terminal_width_padding(
        self, 
        mock_terminal_size: Mock, 
        capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that error_print pads output to terminal width."""
        mock_terminal_size.return_value = Mock(columns=80)
        
        print_utils.error_print("Test")
        captured = capsys.readouterr()
        
        # Just verify that terminal size was checked
        mock_terminal_size.assert_called()


class TestLoadProgress:
    def test_load_progress_with_echo_true(self) -> None:
        """Test load_progress with echo=True returns tqdm wrapper."""
        test_iterable = [1, 2, 3, 4, 5]
        result = print_utils.load_progress(test_iterable, "Processing", echo=True)
        
        # Should return a tqdm object
        assert isinstance(result, tqdm.tqdm)
        
        # Verify we can iterate through it
        values = list(result)
        assert values == test_iterable

    def test_load_progress_with_echo_false(self) -> None:
        """Test load_progress with echo=False returns original iterable."""
        test_iterable = [1, 2, 3, 4, 5]
        result = print_utils.load_progress(test_iterable, "Processing", echo=False)
        
        # Should return the original iterable
        assert result is test_iterable

    @patch('tqdm.tqdm')
    def test_load_progress_tqdm_parameters(self, mock_tqdm: Mock) -> None:
        """Test that load_progress passes correct parameters to tqdm."""
        test_iterable = [1, 2, 3]
        text = "Processing items"
        symbol = "►"
        indent = 2
        
        print_utils.load_progress(
            test_iterable, 
            text, 
            symbol=symbol, 
            indent=indent, 
            echo=True,
            total=3,  # Additional tqdm parameter
            unit="item"  # Additional tqdm parameter
        )
        
        mock_tqdm.assert_called_once_with(
            test_iterable,
            f"{' ' * indent}[{symbol}] {text}",
            total=3,
            unit="item",
            leave=False,
            position=0,
            file=sys.stdout
        )

    def test_load_progress_default_symbol_and_indent(self) -> None:
        """Test load_progress with default symbol and indent."""
        test_iterable = [1, 2, 3]
        result = print_utils.load_progress(test_iterable, "Test", echo=True)
        
        # Should use default symbol (*) and no indent
        assert isinstance(result, tqdm.tqdm)
        # The description should start with "[*] Test"
        assert result.desc.startswith("[*] Test")

    def test_load_progress_custom_symbol_and_indent(self) -> None:
        """Test load_progress with custom symbol and indent."""
        test_iterable = [1, 2, 3]
        result = print_utils.load_progress(
            test_iterable, 
            "Custom test", 
            symbol="⟶", 
            indent=4, 
            echo=True
        )
        
        # Should use custom symbol and indent
        assert isinstance(result, tqdm.tqdm)
        assert result.desc == "    [⟶] Custom test"

    def test_load_progress_with_empty_iterable(self) -> None:
        """Test load_progress with empty iterable."""
        empty_iterable = []
        result = print_utils.load_progress(empty_iterable, "Empty", echo=True)
        
        assert isinstance(result, tqdm.tqdm)
        values = list(result)
        assert values == []


class TestFormatNumber:
    def test_format_number_integer(self) -> None:
        """Test format_number with integer values."""
        assert print_utils.format_number(1000) == "1 000"
        assert print_utils.format_number(1234567) == "1 234 567"
        assert print_utils.format_number(999) == "999"

    def test_format_number_float(self) -> None:
        """Test format_number with float values."""
        assert print_utils.format_number(1000.5) == "1 000.5"
        assert print_utils.format_number(1234567.89) == "1 234 567.89"
        assert print_utils.format_number(999.123) == "999.123"

    def test_format_number_zero(self) -> None:
        """Test format_number with zero."""
        assert print_utils.format_number(0) == "0"
        assert print_utils.format_number(0.0) == "0.0"

    def test_format_number_negative(self) -> None:
        """Test format_number with negative values."""
        assert print_utils.format_number(-1000) == "-1 000"
        assert print_utils.format_number(-1234567.89) == "-1 234 567.89"

    def test_format_number_small_values(self) -> None:
        """Test format_number with small values."""
        assert print_utils.format_number(1) == "1"
        assert print_utils.format_number(12) == "12"
        assert print_utils.format_number(123) == "123"

    def test_format_number_large_values(self) -> None:
        """Test format_number with very large values."""
        assert print_utils.format_number(1000000000) == "1 000 000 000"
        assert print_utils.format_number(1234567890.123) == "1 234 567 890.123"

    def test_format_number_decimal_precision(self) -> None:
        """Test format_number preserves decimal precision."""
        assert print_utils.format_number(1000.123456) == "1 000.123456"
        assert print_utils.format_number(5000.0) == "5 000.0"


class TestCursorUp:
    def test_cursor_up_single_line(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test cursor_up with single line."""
        print_utils.cursor_up(1)
        captured = capsys.readouterr()
        
        assert captured.out.strip() == "\x1b[1A"

    def test_cursor_up_multiple_lines(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test cursor_up with multiple lines."""
        print_utils.cursor_up(5)
        captured = capsys.readouterr()
        
        assert captured.out.strip() == "\x1b[5A"

    def test_cursor_up_zero_lines(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test cursor_up with zero lines."""
        print_utils.cursor_up(0)
        captured = capsys.readouterr()
        
        assert captured.out.strip() == "\x1b[0A"

    def test_cursor_up_large_number(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test cursor_up with large number of lines."""
        print_utils.cursor_up(100)
        captured = capsys.readouterr()
        
        assert captured.out.strip() == "\x1b[100A"


class TestIntegration:
    """Integration tests that test multiple functions together."""
    
    def test_load_done_sequence(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test typical sequence of load_print followed by done_print."""
        print_utils.load_print("Processing...")
        print_utils.done_print("Completed successfully")
        
        captured = capsys.readouterr()
        
        # Should contain both messages with appropriate formatting
        assert "[*]" in captured.out
        assert "Processing..." in captured.out
        assert "[+]" in captured.out
        assert "Completed successfully" in captured.out

    def test_progress_with_format_number(self) -> None:
        """Test using load_progress with format_number for display."""
        items = list(range(1000))
        formatted_total = print_utils.format_number(len(items))
        
        progress = print_utils.load_progress(
            items, 
            f"Processing {formatted_total} items", 
            echo=True
        )
        
        assert isinstance(progress, tqdm.tqdm)
        assert "1 000 items" in progress.desc

    @patch('shutil.get_terminal_size')
    def test_all_print_functions_respect_terminal_width(
        self, 
        mock_terminal_size: Mock, 
        capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that all print functions respect terminal width."""
        mock_terminal_size.return_value = Mock(columns=50)
        
        print_utils.load_print("Test message")
        print_utils.done_print("Test message")  
        print_utils.error_print("Test message")
        
        captured = capsys.readouterr()
        
        # Just verify that terminal size was checked multiple times
        assert mock_terminal_size.call_count >= 3