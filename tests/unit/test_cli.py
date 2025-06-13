from pathlib import Path
from unittest.mock import Mock, patch
from typer.testing import CliRunner

import pytest
import typer

from src import cli, config


class TestRunCli:
    def test_run_cli(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main CLI entry point."""
        mock_init_cli = Mock()
        mock_cli_instance = Mock()
        mock_init_cli.return_value = mock_cli_instance
        
        monkeypatch.setattr("src.cli._init_cli", mock_init_cli)
        
        cli.run_cli()
        
        mock_init_cli.assert_called_once()
        mock_cli_instance.assert_called_once()


class TestInitCli:
    def test_init_cli(self) -> None:
        """Test CLI initialization and command registration."""
        cli_app = cli._init_cli()
        
        assert isinstance(cli_app, typer.Typer)
        
        # Check that commands are registered
        command_names = [cmd.name for cmd in cli_app.registered_commands]
        expected_commands = ["create", "c", "run", "r", "dashboard", "d", "clean", "cc", "analyze", "a"]
        
        for cmd in expected_commands:
            assert cmd in command_names


class TestCreateOrUpdate:
    def test_create_new_config(
        self, 
        cli_runner: CliRunner, 
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test creating a new config file."""
        # Create fresh directory structure without existing files
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Change working directory to the temporary path
        original_cwd = Path.cwd()
        monkeypatch.chdir(tmp_path)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["create", "config/unique_new_test"])
        
        assert result.exit_code == 0
        assert "Created config config/unique_new_test.yml" in result.output
        
        # Check if file was created in the config directory
        test_file = tmp_path / "config" / "unique_new_test.yml"
        assert test_file.exists()

    def test_update_existing_config(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test updating an existing config file."""
        # Create a config directory and copy a test config
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        # Create an existing config file
        existing_config = config_dir / "existing_test.yml"
        existing_config.write_text("""grid: {}
water:
  water_level: 1.5
breakwater:
  enable: false
vegetation:
  enable: false
numeric:
  n_waves: 30
""")
        
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        monkeypatch.chdir(tmp_path)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["create", "config/existing_test.yml"])
        
        assert result.exit_code == 0
        assert "Updated config config/existing_test.yml" in result.output

    def test_create_multiple_configs(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test creating multiple config files."""
        # Create fresh directory structure without existing files
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Change working directory to the temporary path
        monkeypatch.chdir(tmp_path)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["create", "config/multi_test1", "config/multi_test2.yml"])
        
        assert result.exit_code == 0
        assert "Created config config/multi_test1.yml" in result.output
        assert "Created config config/multi_test2.yml" in result.output
        
        assert (config_dir / "multi_test1.yml").exists()
        assert (config_dir / "multi_test2.yml").exists()

    def test_create_with_short_alias(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test creating config with short alias 'c'."""
        # Create fresh directory structure without existing files
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        monkeypatch.chdir(tmp_path)  # Ensure working directory is the temp path
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["c", "config/test_alias_config"])
        
        assert result.exit_code == 0
        assert ("Created config config/test_alias_config.yml" in result.output or 
                "Updated config config/test_alias_config.yml" in result.output)
        
        # Verify the file was created in the temp directory
        test_file = tmp_path / "config" / "test_alias_config.yml"
        assert test_file.exists()


class TestRun:
    def test_run_simulation(
        self,
        cli_runner: CliRunner,
        minimal_config_file: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test running a simulation."""
        monkeypatch.setattr("src.cli.root_dir", minimal_config_file.parent.parent.parent)
        
        # Mock the run_simulation function
        mock_run_simulation = Mock()
        monkeypatch.setattr("src.cli.run_simulation", mock_run_simulation)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["run", str(minimal_config_file)])
        
        assert result.exit_code == 0
        mock_run_simulation.assert_called_once()

    def test_run_multiple_simulations(
        self,
        cli_runner: CliRunner,
        minimal_config_file: Path,
        full_config_file: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test running multiple simulations."""
        monkeypatch.setattr("src.cli.root_dir", minimal_config_file.parent.parent.parent)
        
        # Mock the run_simulation function
        mock_run_simulation = Mock()
        monkeypatch.setattr("src.cli.run_simulation", mock_run_simulation)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["run", str(minimal_config_file), str(full_config_file)])
        
        assert result.exit_code == 0
        assert mock_run_simulation.call_count == 2

    def test_run_with_short_alias(
        self,
        cli_runner: CliRunner,
        minimal_config_file: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test running simulation with short alias 'r'."""
        monkeypatch.setattr("src.cli.root_dir", minimal_config_file.parent.parent.parent)
        
        # Mock the run_simulation function
        mock_run_simulation = Mock()
        monkeypatch.setattr("src.cli.run_simulation", mock_run_simulation)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["r", str(minimal_config_file)])
        
        assert result.exit_code == 0
        mock_run_simulation.assert_called_once()


class TestRunDashboard:
    def test_run_dashboard(
        self, 
        cli_runner: CliRunner,
        mock_dashboard_server: None
    ) -> None:
        """Test running the dashboard."""
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["dashboard"])
        
        assert result.exit_code == 0

    def test_run_dashboard_short_alias(
        self,
        cli_runner: CliRunner,
        mock_dashboard_server: None
    ) -> None:
        """Test running dashboard with short alias 'd'."""
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["d"])
        
        assert result.exit_code == 0


class TestClean:
    def test_clean_no_simulations_dir(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test clean when no simulations directory exists."""
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["clean"])
        
        assert result.exit_code == 0
        assert "No simulations directory found" in result.output

    def test_clean_no_orphaned_dirs(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test clean when no orphaned directories exist."""
        # Create directories
        config_dir = tmp_path / "config"
        simulations_dir = tmp_path / "simulations"
        config_dir.mkdir()
        simulations_dir.mkdir()
        
        # Create a valid config and simulation
        cfg = config.Config(name="test")
        config_file = config_dir / "test.yml"
        config.write_config(cfg, config_file)
        
        # Read config back to get the actual hash after writing
        cfg_read = config.read_config(config_file)
        sim_dir = simulations_dir / f"test_{cfg_read.hash}"
        sim_dir.mkdir()
        
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["clean"])
        
        assert result.exit_code == 0
        assert "No orphaned simulation directories found" in result.output

    def test_clean_with_orphaned_dirs_dry_run(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test clean with orphaned directories using dry run."""
        # Create directories
        config_dir = tmp_path / "config"
        simulations_dir = tmp_path / "simulations"
        config_dir.mkdir()
        simulations_dir.mkdir()
        
        # Create orphaned simulation directory
        orphaned_dir = simulations_dir / "old_simulation_abcd1234"
        orphaned_dir.mkdir()
        
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["clean", "--dry-run"])
        
        assert result.exit_code == 0
        assert "Found 1 orphaned simulation directories" in result.output
        assert "Dry run complete" in result.output
        assert orphaned_dir.exists()  # Should not be deleted

    def test_clean_with_orphaned_dirs_force(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test clean with orphaned directories using force flag."""
        # Create directories
        config_dir = tmp_path / "config"
        simulations_dir = tmp_path / "simulations"
        config_dir.mkdir()
        simulations_dir.mkdir()
        
        # Create orphaned simulation directories
        orphaned_dir1 = simulations_dir / "old_simulation_abcd1234"
        orphaned_dir2 = simulations_dir / "another_old_efgh5678"
        orphaned_dir1.mkdir()
        orphaned_dir2.mkdir()
        
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["clean", "--force"])
        
        assert result.exit_code == 0
        assert "Found 2 orphaned simulation directories" in result.output
        assert "Deleted 2 orphaned simulation directories" in result.output
        assert not orphaned_dir1.exists()
        assert not orphaned_dir2.exists()

    def test_clean_with_invalid_dir_name(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test clean with simulation directory that has invalid name format."""
        # Create directories
        config_dir = tmp_path / "config"
        simulations_dir = tmp_path / "simulations"
        config_dir.mkdir()
        simulations_dir.mkdir()
        
        # Create directory with invalid name format
        invalid_dir = simulations_dir / "invalid_name_format"
        invalid_dir.mkdir()
        
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["clean", "--force"])
        
        assert result.exit_code == 0
        assert "Found 1 orphaned simulation directories" in result.output

    def test_clean_with_short_alias(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test clean with short alias 'cc'."""
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["cc"])
        
        assert result.exit_code == 0

    def test_clean_config_read_error(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test clean when config file cannot be read."""
        # Create directories
        config_dir = tmp_path / "config"
        simulations_dir = tmp_path / "simulations"
        config_dir.mkdir()
        simulations_dir.mkdir()
        
        # Create invalid config file
        invalid_config = config_dir / "invalid.yml"
        invalid_config.write_text("invalid: yaml: content:")
        
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["clean"])
        
        assert result.exit_code == 0
        # Should handle the error gracefully

    def test_clean_deletion_error(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test clean when directory deletion fails."""
        # Create directories
        config_dir = tmp_path / "config"
        simulations_dir = tmp_path / "simulations"
        config_dir.mkdir()
        simulations_dir.mkdir()
        
        # Create orphaned directory
        orphaned_dir = simulations_dir / "old_simulation_abcd1234"
        orphaned_dir.mkdir()
        
        # Mock shutil.rmtree to raise an exception
        mock_rmtree = Mock(side_effect=OSError("Permission denied"))
        monkeypatch.setattr("shutil.rmtree", mock_rmtree)
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["clean", "--force"])
        
        assert result.exit_code == 0
        assert "Deleted 0 orphaned simulation directories" in result.output


class TestAnalyze:
    def test_analyze_successful(
        self,
        cli_runner: CliRunner,
        minimal_config_file: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test successful analysis."""
        # Set up temporary environment
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Read the config to get the correct hash
        cfg = config.read_config(minimal_config_file)
        # Create the simulation directory with the correct hash
        simulations_dir = tmp_path / "simulations"
        sim_dir = simulations_dir / f"{cfg.name}_{cfg.hash}"
        sim_dir.mkdir(parents=True, exist_ok=True)
        (sim_dir / "swash").mkdir(exist_ok=True)
        
        # Mock analyze_simulation function
        mock_analyze = Mock(return_value={"plot_file": "test_plot.png"})
        with patch.dict('sys.modules', {'src.analysis': Mock(analyze_simulation=mock_analyze)}):
            app = cli._init_cli()
            result = cli_runner.invoke(app, ["analyze", str(minimal_config_file)])
        
        assert result.exit_code == 0
        assert "Analysis complete" in result.output
        mock_analyze.assert_called_once()

    def test_analyze_simulation_not_found(
        self,
        cli_runner: CliRunner,
        minimal_config_file: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test analysis when simulation directory doesn't exist."""
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["analyze", str(minimal_config_file)])
        
        assert result.exit_code == 0
        assert "Simulation directory not found" in result.output

    def test_analyze_swash_dir_not_found(
        self,
        cli_runner: CliRunner,
        minimal_config_file: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test analysis when SWASH directory doesn't exist."""
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Create simulation directory but not swash subdirectory
        cfg = config.read_config(minimal_config_file)
        simulations_dir = tmp_path / "simulations"
        sim_dir = simulations_dir / f"{cfg.name}_{cfg.hash}"
        sim_dir.mkdir(parents=True, exist_ok=True)
        # Don't create swash directory
        
        app = cli._init_cli()
        result = cli_runner.invoke(app, ["analyze", str(minimal_config_file)])
        
        assert result.exit_code == 0
        assert "SWASH output directory not found" in result.output

    def test_analyze_with_error_result(
        self,
        cli_runner: CliRunner,
        minimal_config_file: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test analysis that returns error result."""
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Read the config to get the correct hash
        cfg = config.read_config(minimal_config_file)
        # Create the simulation directory with the correct hash
        simulations_dir = tmp_path / "simulations"
        sim_dir = simulations_dir / f"{cfg.name}_{cfg.hash}"
        sim_dir.mkdir(parents=True, exist_ok=True)
        (sim_dir / "swash").mkdir(exist_ok=True)
        
        # Mock analyze_simulation to return error
        mock_analyze = Mock(return_value={"error": "Analysis failed"})
        with patch.dict('sys.modules', {'src.analysis': Mock(analyze_simulation=mock_analyze)}):
            app = cli._init_cli()
            result = cli_runner.invoke(app, ["analyze", str(minimal_config_file)])
        
        assert result.exit_code == 0
        assert "Analysis failed" in result.output

    def test_analyze_exception(
        self,
        cli_runner: CliRunner,
        minimal_config_file: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test analysis that raises exception."""
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Read the config to get the correct hash
        cfg = config.read_config(minimal_config_file)
        # Create the simulation directory with the correct hash
        simulations_dir = tmp_path / "simulations"
        sim_dir = simulations_dir / f"{cfg.name}_{cfg.hash}"
        sim_dir.mkdir(parents=True, exist_ok=True)
        (sim_dir / "swash").mkdir(exist_ok=True)
        
        # Mock analyze_simulation to raise exception
        mock_analyze = Mock(side_effect=Exception("Unexpected error"))
        with patch.dict('sys.modules', {'src.analysis': Mock(analyze_simulation=mock_analyze)}):
            app = cli._init_cli()
            result = cli_runner.invoke(app, ["analyze", str(minimal_config_file)])
        
        assert result.exit_code == 0
        assert "Analysis failed" in result.output

    def test_analyze_with_short_alias(
        self,
        cli_runner: CliRunner,
        minimal_config_file: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test analysis with short alias 'a'."""
        monkeypatch.setattr("src.cli.root_dir", tmp_path)
        
        # Read the config to get the correct hash
        cfg = config.read_config(minimal_config_file)
        # Create the simulation directory with the correct hash
        simulations_dir = tmp_path / "simulations"
        sim_dir = simulations_dir / f"{cfg.name}_{cfg.hash}"
        sim_dir.mkdir(parents=True, exist_ok=True)
        (sim_dir / "swash").mkdir(exist_ok=True)
        
        # Mock analyze_simulation function
        mock_analyze = Mock(return_value={})
        with patch.dict('sys.modules', {'src.analysis': Mock(analyze_simulation=mock_analyze)}):
            app = cli._init_cli()
            result = cli_runner.invoke(app, ["a", str(minimal_config_file)])
        
        assert result.exit_code == 0


class TestExpandPaths:
    def test_expand_paths_single_file(self, tmp_config_dir: Path) -> None:
        """Test expanding a single file path."""
        config_file = tmp_config_dir / "test.yml"
        config_file.write_text("test content")
        
        result = cli._expand_paths([str(config_file)])
        assert result == [config_file]

    def test_expand_paths_multiple_files(self, tmp_config_dir: Path) -> None:
        """Test expanding multiple file paths."""
        file1 = tmp_config_dir / "test1.yml"
        file2 = tmp_config_dir / "test2.yml"
        file1.write_text("test1")
        file2.write_text("test2")
        
        result = cli._expand_paths([str(file1), str(file2)])
        assert len(result) == 2
        assert file1 in result
        assert file2 in result

    def test_expand_paths_directory(self, tmp_config_dir: Path) -> None:
        """Test expanding directory path."""
        file1 = tmp_config_dir / "test1.yml"
        file2 = tmp_config_dir / "test2.yml"
        file1.write_text("test1")
        file2.write_text("test2")
        
        result = cli._expand_paths([str(tmp_config_dir)])
        assert len(result) == 2
        assert file1 in result
        assert file2 in result

    def test_expand_paths_glob_pattern(self, tmp_config_dir: Path) -> None:
        """Test expanding glob pattern."""
        file1 = tmp_config_dir / "test1.yml"
        file2 = tmp_config_dir / "test2.yml"
        other_file = tmp_config_dir / "test.txt"
        file1.write_text("test1")
        file2.write_text("test2")
        other_file.write_text("other")
        
        pattern = str(tmp_config_dir / "*.yml")
        result = cli._expand_paths([pattern])
        assert len(result) == 2
        assert file1 in result
        assert file2 in result
        assert other_file not in result

    def test_expand_paths_nested_directory(self, tmp_path: Path) -> None:
        """Test expanding nested directory structure."""
        nested_dir = tmp_path / "nested"
        nested_dir.mkdir()
        
        file1 = tmp_path / "test1.yml"
        file2 = nested_dir / "test2.yml"
        file1.write_text("test1")
        file2.write_text("test2")
        
        result = cli._expand_paths([str(tmp_path)])
        assert len(result) == 2
        assert file1 in result
        assert file2 in result

    def test_expand_paths_mixed_input(self, tmp_path: Path) -> None:
        """Test expanding mixed file and directory paths."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        file1 = tmp_path / "direct.yml"
        file2 = config_dir / "nested.yml"
        file1.write_text("direct")
        file2.write_text("nested")
        
        result = cli._expand_paths([str(file1), str(config_dir)])
        assert len(result) == 2
        assert file1 in result
        assert file2 in result

    def test_expand_paths_duplicates_removed(self, tmp_config_dir: Path) -> None:
        """Test that duplicate paths are removed."""
        config_file = tmp_config_dir / "test.yml"
        config_file.write_text("test")
        
        result = cli._expand_paths([str(config_file), str(config_file)])
        assert len(result) == 1
        assert result[0] == config_file

    def test_expand_paths_sorted_output(self, tmp_config_dir: Path) -> None:
        """Test that output paths are sorted."""
        file_z = tmp_config_dir / "z_test.yml"
        file_a = tmp_config_dir / "a_test.yml"
        file_z.write_text("z")
        file_a.write_text("a")
        
        result = cli._expand_paths([str(file_z), str(file_a)])
        assert result == [file_a, file_z]  # Should be sorted

    def test_expand_paths_nonexistent_file(self) -> None:
        """Test expanding nonexistent file path."""
        nonexistent = Path("/nonexistent/file.yml")
        result = cli._expand_paths([str(nonexistent)])
        assert result == [nonexistent]  # Should include even if doesn't exist