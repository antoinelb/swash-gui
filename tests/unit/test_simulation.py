import subprocess
import sys
import threading
import time
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import numpy as np
import pytest
import tqdm

from src import config, simulation


class TestRunSimulation:
    def test_run_simulation_success(
        self,
        full_config: config.Config,
        tmp_simulations_dir: Path,
        input_template: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test successful simulation run."""
        # Mock dependencies
        monkeypatch.setattr(
            "src.simulation.root_dir", tmp_simulations_dir.parent
        )
        
        # Mock all the file creation functions
        mock_create_bathymetry = Mock()
        mock_create_porosity = Mock()
        mock_create_vegetation = Mock()
        mock_create_input = Mock()
        mock_execute_swash = Mock(return_value=True)
        
        monkeypatch.setattr("src.simulation._create_bathymetry_file", mock_create_bathymetry)
        monkeypatch.setattr("src.simulation._create_porosity_file", mock_create_porosity)
        monkeypatch.setattr("src.simulation._create_vegetation_file", mock_create_vegetation)
        monkeypatch.setattr("src.simulation._create_input_file", mock_create_input)
        monkeypatch.setattr("src.simulation._execute_swash", mock_execute_swash)
        
        # Mock analysis import
        mock_analyze = Mock()
        with patch.dict('sys.modules', {'src.analysis': Mock(analyze_simulation=mock_analyze)}):
            simulation.run_simulation(full_config)
        
        # Verify file creation functions were called
        mock_create_bathymetry.assert_called_once()
        mock_create_porosity.assert_called_once()
        mock_create_vegetation.assert_called_once()
        mock_create_input.assert_called_once()
        mock_execute_swash.assert_called_once()
        mock_analyze.assert_called_once()

    def test_run_simulation_disabled_breakwater(
        self,
        minimal_config: config.Config,
        tmp_simulations_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test simulation with disabled breakwater."""
        monkeypatch.setattr(
            "src.simulation.root_dir", tmp_simulations_dir.parent
        )
        
        # Mock file creation functions
        mock_create_bathymetry = Mock()
        mock_create_porosity = Mock()
        mock_create_input = Mock()
        mock_execute_swash = Mock(return_value=True)
        
        monkeypatch.setattr("src.simulation._create_bathymetry_file", mock_create_bathymetry)
        monkeypatch.setattr("src.simulation._create_porosity_file", mock_create_porosity)
        monkeypatch.setattr("src.simulation._create_input_file", mock_create_input)
        monkeypatch.setattr("src.simulation._execute_swash", mock_execute_swash)
        
        # Mock analysis module
        with patch.dict('sys.modules', {'src.analysis': Mock(analyze_simulation=Mock())}):
            simulation.run_simulation(minimal_config)
        
        # Verify only bathymetry and input files are created
        mock_create_bathymetry.assert_called_once()
        mock_create_porosity.assert_not_called()
        mock_create_input.assert_called_once()

    def test_run_simulation_analysis_failure(
        self,
        full_config: config.Config,
        tmp_simulations_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test simulation with analysis failure."""
        monkeypatch.setattr(
            "src.simulation.root_dir", tmp_simulations_dir.parent
        )
        
        # Mock successful simulation but failing analysis
        monkeypatch.setattr("src.simulation._create_bathymetry_file", Mock())
        monkeypatch.setattr("src.simulation._create_porosity_file", Mock())
        monkeypatch.setattr("src.simulation._create_vegetation_file", Mock())
        monkeypatch.setattr("src.simulation._create_input_file", Mock())
        monkeypatch.setattr("src.simulation._execute_swash", Mock(return_value=True))
        
        # Mock failing analysis
        failing_analyze = Mock(side_effect=Exception("Analysis failed"))
        with patch.dict('sys.modules', {'src.analysis': Mock(analyze_simulation=failing_analyze)}):
            # Should not raise exception, just log error
            simulation.run_simulation(full_config)


class TestCreateBathymetryFile:
    def test_create_bathymetry_file(
        self, full_config: config.Config, tmp_path: Path
    ) -> None:
        """Test bathymetry file creation."""
        simulation._create_bathymetry_file(full_config, simulation_dir=tmp_path)
        
        bathymetry_file = tmp_path / "bathymetry.txt"
        assert bathymetry_file.exists()
        
        # Check content - should include breakwater profile when enabled
        data = np.loadtxt(bathymetry_file)
        expected_length = full_config.grid.nx_cells + 1
        assert len(data) == expected_length
        
        if full_config.breakwater.enable:
            # Should have non-zero elevations where breakwater exists
            assert np.max(data) > 0.0
            assert np.max(data) == full_config.breakwater.crest_height
        else:
            # Should be all zeros if no breakwater
            assert np.all(data == 0.0)


class TestCreatePorosityFile:
    def test_create_porosity_file(
        self, full_config: config.Config, tmp_path: Path
    ) -> None:
        """Test porosity file creation."""
        simulation._create_porosity_file(full_config, simulation_dir=tmp_path)
        
        porosity_file = tmp_path / "porosity.txt"
        assert porosity_file.exists()
        
        data = np.loadtxt(porosity_file)
        expected_length = full_config.grid.nx_cells + 1
        assert len(data) == expected_length
        
        # Check that values within breakwater range have correct porosity
        x = np.linspace(0, full_config.grid.length, full_config.grid.nx_cells + 1)
        breakwater_mask = (x >= full_config.breakwater.breakwater_start_position) & (
            x <= full_config.breakwater_end_position
        )
        
        # Breakwater region should have breakwater porosity
        assert np.all(data[breakwater_mask] == full_config.breakwater.porosity)
        # Outside breakwater should have porosity of 1.0
        assert np.all(data[~breakwater_mask] == 1.0)




class TestCreateVegetationFile:
    def test_create_vegetation_file_single_type(
        self, vegetation_config: config.VegetationConfig, tmp_path: Path
    ) -> None:
        """Test vegetation file creation with single vegetation type."""
        # Create a config with vegetation enabled
        cfg = config.Config(
            name="test",
            vegetation=vegetation_config,
            breakwater=config.BreakwaterConfig(
                enable=True,
                breakwater_start_position=70.0,
                crest_height=2.0,
                crest_length=2.0,
                slope=2.0,
            ),
        )
        cfg.vegetation.enable = True
        
        simulation._create_vegetation_file(cfg, simulation_dir=tmp_path)
        
        veg_file = tmp_path / "vegetation_density.txt"
        assert veg_file.exists()
        
        data = np.loadtxt(veg_file)
        # Should have vegetation only on crest, zeros elsewhere
        assert np.any(data > 0)  # Some non-zero values
        assert np.any(data == 0)  # Some zero values

    def test_create_vegetation_file_two_types_half(self, tmp_path: Path) -> None:
        """Test vegetation file creation with two types in half distribution."""
        other_type = config.VegetationType(
            plant_height=0.3,
            plant_diameter=0.01,
            plant_density=100.0,
            drag_coefficient=1.0,
        )
        
        cfg = config.Config(
            name="test",
            vegetation=config.VegetationConfig(
                enable=True,
                other_type=other_type,
                distribution="half",
                type_fraction=0.5,
            ),
            breakwater=config.BreakwaterConfig(
                enable=True,
                breakwater_start_position=70.0,
                crest_height=2.0,
                crest_length=2.0,
                slope=2.0,
            ),
        )
        
        simulation._create_vegetation_file(cfg, simulation_dir=tmp_path)
        
        veg_file = tmp_path / "vegetation_density.txt"
        assert veg_file.exists()
        
        data = np.loadtxt(veg_file)
        # Should have two different non-zero values
        unique_values = np.unique(data[data > 0])
        assert len(unique_values) == 2

    def test_create_vegetation_file_two_types_alternating(
        self, tmp_path: Path
    ) -> None:
        """Test vegetation file creation with two types in alternating distribution."""
        other_type = config.VegetationType(
            plant_height=0.3,
            plant_diameter=0.01,
            plant_density=100.0,
            drag_coefficient=1.0,
        )
        
        cfg = config.Config(
            name="test",
            vegetation=config.VegetationConfig(
                enable=True,
                other_type=other_type,
                distribution="alternating",
                type_fraction=0.3,
            ),
            breakwater=config.BreakwaterConfig(
                enable=True,
                breakwater_start_position=70.0,
                crest_height=2.0,
                crest_length=2.0,
                slope=2.0,
            ),
        )
        
        simulation._create_vegetation_file(cfg, simulation_dir=tmp_path)
        
        veg_file = tmp_path / "vegetation_density.txt"
        assert veg_file.exists()


class TestCreateInputFile:
    def test_create_input_file(
        self,
        full_config: config.Config,
        input_template: Path,
        tmp_path: Path,
    ) -> None:
        """Test INPUT file creation from template."""
        simulation._create_input_file(
            full_config,
            simulation_dir=tmp_path,
            template_dir=input_template.parent,
        )
        
        input_file = tmp_path / "INPUT"
        assert input_file.exists()
        
        content = input_file.read_text()
        # Check that template was rendered with config values
        assert str(full_config.water.water_level) in content
        assert str(full_config.grid.length) in content
        assert str(full_config.grid.nx_cells) in content

    def test_create_input_file_template_rendering(
        self,
        full_config: config.Config,
        tmp_path: Path,
    ) -> None:
        """Test that Jinja2 template rendering works correctly."""
        # Create a simple template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "INPUT"
        template_content = """PROJECT '{{ name }}' '{{ project_nr }}'
SET level={{ water.water_level }}
CGRID CURV 0 0 0 {{ grid.length }} 0 {{ grid.nx_cells }} 0 0
{% if breakwater.enable %}
BREAKWATER ENABLED
{% endif %}
"""
        template_file.write_text(template_content)
        
        simulation._create_input_file(
            full_config,
            simulation_dir=tmp_path,
            template_dir=template_dir,
        )
        
        input_file = tmp_path / "INPUT"
        content = input_file.read_text()
        
        assert f"PROJECT '{full_config.name}'" in content
        assert f"SET level={full_config.water.water_level}" in content
        assert f"{full_config.grid.length}" in content
        assert f"{full_config.grid.nx_cells}" in content
        assert "BREAKWATER ENABLED" in content


class TestExecuteSwash:
    def test_execute_swash_success(
        self,
        full_config: config.Config,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test successful SWASH execution."""
        # Mock subprocess.Popen
        mock_process = Mock()
        mock_process.poll.return_value = None  # Running
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        
        mock_popen = Mock(return_value=mock_process)
        monkeypatch.setattr("subprocess.Popen", mock_popen)
        
        # Mock progress monitoring
        monkeypatch.setattr("src.simulation.threading.Thread", Mock())
        monkeypatch.setattr("src.simulation.tqdm.tqdm", Mock())
        
        # Mock error checking
        monkeypatch.setattr("src.simulation._check_swash_errors", Mock(return_value=[]))
        
        result = simulation._execute_swash(full_config, simulation_dir=tmp_path)
        
        assert result is True
        mock_popen.assert_called_once()

    def test_execute_swash_failure(
        self,
        full_config: config.Config,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test SWASH execution failure."""
        # Mock subprocess.Popen with failure
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.communicate.return_value = ("", "Error message")
        mock_process.returncode = 1
        
        mock_popen = Mock(return_value=mock_process)
        monkeypatch.setattr("subprocess.Popen", mock_popen)
        
        # Mock other dependencies
        monkeypatch.setattr("src.simulation.threading.Thread", Mock())
        monkeypatch.setattr("src.simulation.tqdm.tqdm", Mock())
        monkeypatch.setattr("src.simulation._check_swash_errors", Mock(return_value=[]))
        
        result = simulation._execute_swash(full_config, simulation_dir=tmp_path)
        
        assert result is False

    def test_execute_swash_file_not_found(
        self,
        full_config: config.Config,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test SWASH execution when executable not found."""
        # Mock subprocess.Popen to raise FileNotFoundError
        mock_popen = Mock(side_effect=FileNotFoundError("swash not found"))
        monkeypatch.setattr("subprocess.Popen", mock_popen)
        
        result = simulation._execute_swash(full_config, simulation_dir=tmp_path)
        
        assert result is False

    def test_execute_swash_timeout(
        self,
        full_config: config.Config,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test SWASH execution timeout."""
        # Mock subprocess.Popen to raise TimeoutExpired
        mock_process = Mock()
        mock_process.communicate.side_effect = subprocess.TimeoutExpired("swash", 3600)
        mock_process.kill = Mock()
        
        mock_popen = Mock(return_value=mock_process)
        monkeypatch.setattr("subprocess.Popen", mock_popen)
        
        result = simulation._execute_swash(full_config, simulation_dir=tmp_path)
        
        assert result is False
        mock_process.kill.assert_called_once()

    def test_execute_swash_with_errors(
        self,
        full_config: config.Config,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test SWASH execution with errors detected."""
        # Mock successful process but with errors
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        
        mock_popen = Mock(return_value=mock_process)
        monkeypatch.setattr("subprocess.Popen", mock_popen)
        
        # Mock dependencies
        monkeypatch.setattr("src.simulation.threading.Thread", Mock())
        monkeypatch.setattr("src.simulation.tqdm.tqdm", Mock())
        
        # Mock error checking to return errors
        monkeypatch.setattr(
            "src.simulation._check_swash_errors", 
            Mock(return_value=["Error 1", "Error 2"])
        )
        
        result = simulation._execute_swash(full_config, simulation_dir=tmp_path)
        
        assert result is False


class TestCheckSwashErrors:
    def test_check_swash_errors_no_errors(self, tmp_path: Path) -> None:
        """Test error checking with no errors."""
        errors = simulation._check_swash_errors(tmp_path)
        assert errors == []

    def test_check_swash_errors_errfile(self, tmp_path: Path) -> None:
        """Test error checking with Errfile errors."""
        errfile = tmp_path / "Errfile"
        errfile.write_text("Something went wrong")
        
        errors = simulation._check_swash_errors(tmp_path)
        assert len(errors) == 1
        assert "Errfile: Something went wrong" in errors[0]

    def test_check_swash_errors_print_file(self, tmp_path: Path) -> None:
        """Test error checking with PRINT file errors."""
        print_file = tmp_path / "PRINT"
        print_content = """Normal output
** Severe error: Division by zero
More normal output  
** Error: Invalid input
Final output
"""
        print_file.write_text(print_content)
        
        errors = simulation._check_swash_errors(tmp_path)
        assert len(errors) == 2
        assert any("Severe error: Division by zero" in error for error in errors)
        assert any("Error: Invalid input" in error for error in errors)
        assert any("PRINT line 2:" in error for error in errors)
        assert any("PRINT line 4:" in error for error in errors)

    def test_check_swash_errors_empty_errfile(self, tmp_path: Path) -> None:
        """Test error checking with empty Errfile."""
        errfile = tmp_path / "Errfile"
        errfile.write_text("")
        
        errors = simulation._check_swash_errors(tmp_path)
        assert errors == []

    def test_check_swash_errors_file_read_exception(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test error checking with file read exceptions."""
        errfile = tmp_path / "Errfile"
        errfile.write_text("Some error")
        
        # Mock open to raise exception
        original_open = open
        def mock_open_func(*args, **kwargs):
            if "Errfile" in str(args[0]):
                raise IOError("Cannot read file")
            return original_open(*args, **kwargs)
        
        monkeypatch.setattr("builtins.open", mock_open_func)
        
        # Should not raise exception, just return empty list
        errors = simulation._check_swash_errors(tmp_path)
        assert errors == []