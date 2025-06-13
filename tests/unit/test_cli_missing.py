"""Tests for missing cli.py coverage lines."""

import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
import typer

from src import cli, config


class TestCleanMissingCoverage:
    """Test cases to cover missing lines in clean command."""

    def test_clean_skip_non_directory_items(
        self, 
        tmp_path: Path, 
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that non-directory items are skipped (line 150)."""
        # Setup temporary directories
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        simulations_dir = tmp_path / "simulations"
        simulations_dir.mkdir()
        
        # Create a file (not directory) in simulations directory
        non_dir_file = simulations_dir / "not_a_directory.txt"
        non_dir_file.write_text("This is not a directory")
        
        # Create a valid config
        config_file = config_dir / "test.yml"
        test_config = config.Config(name="test")
        config.write_config(test_config, config_file)
        
        # Mock root_dir
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Run clean command
        cli._clean(dry_run=True, force=False)
        
        # File should still exist (was skipped)
        assert non_dir_file.exists()

    def test_clean_orphaned_directory_bad_name_format(
        self, 
        tmp_path: Path, 
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test orphaned directory with bad name format (lines 155-156)."""
        # Setup temporary directories
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        simulations_dir = tmp_path / "simulations"
        simulations_dir.mkdir()
        
        # Create directory with bad name format (no underscore)
        bad_name_dir = simulations_dir / "badnameformat"
        bad_name_dir.mkdir()
        
        # Create directory with multiple underscores that would fail rsplit
        multi_underscore_dir = simulations_dir / "name_with_multiple_underscores"
        multi_underscore_dir.mkdir()
        
        # Mock root_dir
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Run clean command with dry_run
        cli._clean(dry_run=True, force=False)
        
        # Both directories should still exist (detected as orphaned but not deleted due to dry run)
        assert bad_name_dir.exists()
        assert multi_underscore_dir.exists()

    def test_clean_user_cancels_deletion(
        self, 
        tmp_path: Path, 
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test user canceling deletion when prompted (lines 179-182)."""
        # Setup temporary directories
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        simulations_dir = tmp_path / "simulations"
        simulations_dir.mkdir()
        
        # Create orphaned simulation directory
        orphaned_dir = simulations_dir / "old_simulation_abcd1234"
        orphaned_dir.mkdir()
        
        # Mock root_dir
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Mock typer.confirm to return False (user cancels)
        with patch("typer.confirm", return_value=False) as mock_confirm:
            cli._clean(dry_run=False, force=False)
            
        # Confirm was called
        mock_confirm.assert_called_once_with("Delete these directories?")
        
        # Directory should still exist (deletion was cancelled)
        assert orphaned_dir.exists()

    def test_clean_user_confirms_deletion(
        self, 
        tmp_path: Path, 
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test user confirming deletion when prompted."""
        # Setup temporary directories
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        simulations_dir = tmp_path / "simulations"
        simulations_dir.mkdir()
        
        # Create orphaned simulation directory
        orphaned_dir = simulations_dir / "old_simulation_abcd1234"
        orphaned_dir.mkdir()
        
        # Mock root_dir
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Mock typer.confirm to return True (user confirms)
        with patch("typer.confirm", return_value=True) as mock_confirm:
            cli._clean(dry_run=False, force=False)
            
        # Confirm was called
        mock_confirm.assert_called_once_with("Delete these directories?")
        
        # Directory should be deleted
        assert not orphaned_dir.exists()

    def test_clean_force_skips_confirmation(
        self, 
        tmp_path: Path, 
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that force=True skips confirmation prompt."""
        # Setup temporary directories
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        simulations_dir = tmp_path / "simulations"
        simulations_dir.mkdir()
        
        # Create orphaned simulation directory
        orphaned_dir = simulations_dir / "old_simulation_abcd1234"
        orphaned_dir.mkdir()
        
        # Mock root_dir
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Mock typer.confirm to ensure it's not called
        with patch("typer.confirm") as mock_confirm:
            cli._clean(dry_run=False, force=True)
            
        # Confirm should not be called
        mock_confirm.assert_not_called()
        
        # Directory should be deleted
        assert not orphaned_dir.exists()

    def test_clean_orphaned_directory_with_valid_name_invalid_hash(
        self, 
        tmp_path: Path, 
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test orphaned directory with valid name format but invalid hash."""
        # Setup temporary directories
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        simulations_dir = tmp_path / "simulations"
        simulations_dir.mkdir()
        
        # Create a valid config
        config_file = config_dir / "test.yml"
        test_config = config.Config(name="test")
        config.write_config(test_config, config_file)
        
        # Create simulation directory with valid name but wrong hash
        orphaned_dir = simulations_dir / "test_wronghash"
        orphaned_dir.mkdir()
        
        # Mock root_dir
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Run clean command
        cli._clean(dry_run=False, force=True)
        
        # Directory should be deleted (orphaned due to wrong hash)
        assert not orphaned_dir.exists()

    def test_clean_deletion_error_handling(
        self, 
        tmp_path: Path, 
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test error handling during directory deletion."""
        # Setup temporary directories
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        simulations_dir = tmp_path / "simulations"
        simulations_dir.mkdir()
        
        # Create orphaned simulation directory
        orphaned_dir = simulations_dir / "old_simulation_abcd1234"
        orphaned_dir.mkdir()
        
        # Mock root_dir
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Mock shutil.rmtree to raise an exception
        with patch("shutil.rmtree", side_effect=OSError("Permission denied")):
            cli._clean(dry_run=False, force=True)
        
        # Directory should still exist due to deletion error
        assert orphaned_dir.exists()