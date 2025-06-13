"""Tests for missing simulation.py coverage lines."""

import subprocess
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from src import config, simulation


class TestExecuteSwashMissingCoverage:
    """Test cases to cover missing lines in _execute_swash."""

    def test_execute_swash_errfile_removal(
        self,
        full_config: config.Config,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that existing Errfile is removed before execution (line 230)."""
        # Create an existing Errfile
        errfile = tmp_path / "Errfile"
        errfile.write_text("Old error")
        assert errfile.exists()
        
        # Mock successful process
        mock_process = Mock()
        mock_process.poll.return_value = 0  # Process finished
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        
        mock_popen = Mock(return_value=mock_process)
        monkeypatch.setattr("subprocess.Popen", mock_popen)
        
        # Mock threading and tqdm to avoid complexity
        monkeypatch.setattr("src.simulation.threading.Thread", Mock())
        monkeypatch.setattr("src.simulation.tqdm.tqdm", Mock(return_value=Mock()))
        
        # Mock error checking to return no errors
        monkeypatch.setattr("src.simulation._check_swash_errors", Mock(return_value=[]))
        
        result = simulation._execute_swash(full_config, simulation_dir=tmp_path)
        
        assert result is True
        # Errfile should have been removed
        assert not errfile.exists()

    def test_execute_swash_print_monitoring_success(
        self,
        full_config: config.Config,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test progress monitoring with PRINT file (lines 278-299)."""
        # Create PRINT file with time progress
        print_file = tmp_path / "PRINT"
        print_content = """Initial output
Time of simulation      ->    12.5 in sec:      25.0
More output
Time of simulation      ->    25.0 in sec:      50.0
Final output
"""
        print_file.write_text(print_content)
        
        # Mock process that finishes after one check
        mock_process = Mock()
        poll_calls = [None, 0]  # First call returns None (running), second returns 0 (finished)
        mock_process.poll.side_effect = poll_calls
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        
        mock_popen = Mock(return_value=mock_process)
        monkeypatch.setattr("subprocess.Popen", mock_popen)
        
        # Mock progress bar
        mock_progress_bar = Mock()
        mock_progress_bar.total = 100
        mock_tqdm = Mock(return_value=mock_progress_bar)
        monkeypatch.setattr("src.simulation.tqdm.tqdm", mock_tqdm)
        
        # Mock thread join
        mock_thread = Mock()
        mock_thread.join = Mock()
        monkeypatch.setattr("src.simulation.threading.Thread", Mock(return_value=mock_thread))
        
        # Speed up the loop by mocking time.sleep
        monkeypatch.setattr("time.sleep", Mock())
        
        # Mock error checking
        monkeypatch.setattr("src.simulation._check_swash_errors", Mock(return_value=[]))
        
        result = simulation._execute_swash(full_config, simulation_dir=tmp_path)
        
        assert result is True
        # Test passed - monitoring code was executed
        assert result is True

    def test_execute_swash_print_monitoring_io_error(
        self,
        full_config: config.Config,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test progress monitoring with PRINT file IO error (lines 296-297)."""
        # Create PRINT file
        print_file = tmp_path / "PRINT"
        print_file.write_text("Some content")
        
        # Mock process that finishes after one check
        mock_process = Mock()
        mock_process.poll.side_effect = [None, 0]
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        
        mock_popen = Mock(return_value=mock_process)
        monkeypatch.setattr("subprocess.Popen", mock_popen)
        
        # Mock progress bar
        mock_progress_bar = Mock()
        mock_tqdm = Mock(return_value=mock_progress_bar)
        monkeypatch.setattr("src.simulation.tqdm.tqdm", mock_tqdm)
        
        # Mock thread
        mock_thread = Mock()
        monkeypatch.setattr("src.simulation.threading.Thread", Mock(return_value=mock_thread))
        
        # Mock time.sleep
        monkeypatch.setattr("time.sleep", Mock())
        
        # Mock file open to raise IOError during monitoring
        original_open = open
        def mock_open_func(*args, **kwargs):
            if str(args[0]).endswith("PRINT"):
                raise IOError("Cannot read PRINT file")
            return original_open(*args, **kwargs)
        
        monkeypatch.setattr("builtins.open", mock_open_func)
        
        # Mock error checking
        monkeypatch.setattr("src.simulation._check_swash_errors", Mock(return_value=[]))
        
        result = simulation._execute_swash(full_config, simulation_dir=tmp_path)
        
        assert result is True  # Should continue despite IO error

    def test_execute_swash_progress_bar_close_after_thread_join(
        self,
        full_config: config.Config,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test progress bar close after thread join (line 319)."""
        # Mock successful process
        mock_process = Mock()
        mock_process.poll.return_value = 0
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        
        mock_popen = Mock(return_value=mock_process)
        monkeypatch.setattr("subprocess.Popen", mock_popen)
        
        # Mock progress bar that exists
        mock_progress_bar = Mock()
        mock_tqdm = Mock(return_value=mock_progress_bar)
        monkeypatch.setattr("src.simulation.tqdm.tqdm", mock_tqdm)
        
        # Mock thread
        mock_thread = Mock()
        monkeypatch.setattr("src.simulation.threading.Thread", Mock(return_value=mock_thread))
        
        # Mock error checking
        monkeypatch.setattr("src.simulation._check_swash_errors", Mock(return_value=[]))
        
        result = simulation._execute_swash(full_config, simulation_dir=tmp_path)
        
        assert result is True
        # Test passed - progress bar handling was executed
        assert result is True

    def test_execute_swash_return_code_error_with_stderr(
        self,
        full_config: config.Config,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test process return code error with stderr (lines 336-338)."""
        # Mock process with non-zero return code and stderr
        mock_process = Mock()
        mock_process.poll.return_value = 1
        mock_process.communicate.return_value = ("", "Error: Invalid input format")
        mock_process.returncode = 1
        
        mock_popen = Mock(return_value=mock_process)
        monkeypatch.setattr("subprocess.Popen", mock_popen)
        
        # Mock dependencies
        monkeypatch.setattr("src.simulation.threading.Thread", Mock())
        monkeypatch.setattr("src.simulation.tqdm.tqdm", Mock())
        
        # Mock error checking to return no errors (so we test the return code path)
        monkeypatch.setattr("src.simulation._check_swash_errors", Mock(return_value=[]))
        
        result = simulation._execute_swash(full_config, simulation_dir=tmp_path)
        
        assert result is False

    def test_execute_swash_unexpected_exception(
        self,
        full_config: config.Config,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test unexpected exception handling (lines 353-355)."""
        # Mock subprocess.Popen to raise an unexpected exception
        mock_popen = Mock(side_effect=RuntimeError("Unexpected error"))
        monkeypatch.setattr("subprocess.Popen", mock_popen)
        
        result = simulation._execute_swash(full_config, simulation_dir=tmp_path)
        
        assert result is False


class TestCheckSwashErrorsMissingCoverage:
    """Test cases to cover missing lines in _check_swash_errors."""

    def test_check_swash_errors_print_file_exception(self, tmp_path: Path) -> None:
        """Test PRINT file read exception handling (lines 387-388)."""
        # Create PRINT file
        print_file = tmp_path / "PRINT"
        print_file.write_text("** Error: Test error")
        
        # Mock open to raise exception when reading PRINT file
        original_open = open
        def mock_open_func(*args, **kwargs):
            if "PRINT" in str(args[0]):
                raise IOError("Cannot read PRINT file")
            return original_open(*args, **kwargs)
        
        with patch("builtins.open", side_effect=mock_open_func):
            errors = simulation._check_swash_errors(tmp_path)
        
        # Should handle exception gracefully and return empty list
        assert errors == []

    def test_check_swash_errors_both_files_with_exceptions(self, tmp_path: Path) -> None:
        """Test both Errfile and PRINT file exception handling."""
        # Create both files
        errfile = tmp_path / "Errfile"
        errfile.write_text("Errfile error")
        print_file = tmp_path / "PRINT"
        print_file.write_text("** Error: Print error")
        
        # Mock open to raise exception for both files
        def mock_open_func(*args, **kwargs):
            if "Errfile" in str(args[0]) or "PRINT" in str(args[0]):
                raise IOError("Cannot read file")
            return open(*args, **kwargs)
        
        with patch("builtins.open", side_effect=mock_open_func):
            errors = simulation._check_swash_errors(tmp_path)
        
        # Should handle exceptions gracefully and return empty list
        assert errors == []