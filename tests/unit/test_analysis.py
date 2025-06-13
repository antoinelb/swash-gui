import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import polars as pl
import pytest

from src import analysis, config


class TestAnalyzeSimulation:
    """Test the main analyze_simulation function."""

    def test_analyze_simulation_success(self, tmp_path: Path) -> None:
        """Test successful analysis with all components."""
        # Create test configuration
        cfg = config.Config(
            name="test_simulation",
            water=config.WaterConfig(wave_period=6.0),
            breakwater=config.BreakwaterConfig(enable=True),
            numeric=config.NumericConfig(
                wave_gauge_positions=[20.0, 60.0, 65.0, 80.0, 100.0]
            ),
        )

        # Create test directory structure
        simulation_dir = tmp_path / "test_sim"
        swash_dir = simulation_dir / "swash"
        swash_dir.mkdir(parents=True)
        analysis_dir = simulation_dir / "analysis"
        analysis_dir.mkdir(parents=True)

        # Create test INPUT file
        input_file = swash_dir / "INPUT"
        input_file.write_text("WATLEV OUTPUT 0.0 0.0 0.1 SEC\n")

        # Create test wave gauge files
        test_data = np.array([[0.1, 0.05, 0.02], [0.2, 0.08, 0.03], [0.15, 0.06, 0.025]])
        for i in range(5):
            gauge_file = swash_dir / f"wg{i+1:02d}.txt"
            np.savetxt(gauge_file, test_data, fmt="%.3f")

        # Mock the wave statistics calculation
        with patch(
            "src.analysis.calculate_wave_statistics_for_gauges"
        ) as mock_wave_stats:
            mock_stats = pl.DataFrame(
                {
                    "position": [20.0, 60.0, 65.0, 80.0, 100.0],
                    "significant_wave_height": [0.15, 0.16, 0.14, 0.13, 0.12],
                    "mean_wave_height": [0.12, 0.13, 0.11, 0.10, 0.09],
                    "n_waves": [10, 11, 9, 8, 7],
                }
            )
            mock_wave_stats.return_value = mock_stats

            # Run analysis
            result = analysis.analyze_simulation(simulation_dir, cfg)

            # Verify results
            assert "plot_file" in result
            assert "wave_stats" in result
            assert isinstance(result["wave_stats"], list)
            assert len(result["wave_stats"]) == 5

            # Verify files were created
            assert (analysis_dir / "water_levels_and_x_velocity.png").exists()
            assert (analysis_dir / "water_levels_and_x_velocity.json").exists()
            assert (analysis_dir / "wave_statistics.csv").exists()

            # Verify data.csv was created
            assert (swash_dir / "data.csv").exists()

    def test_analyze_simulation_missing_plot_file(self, tmp_path: Path) -> None:
        """Test analysis when plot file is not created."""
        cfg = config.Config(name="test_simulation")
        simulation_dir = tmp_path / "test_sim"
        swash_dir = simulation_dir / "swash"
        swash_dir.mkdir(parents=True)

        # Create minimal test files
        input_file = swash_dir / "INPUT"
        input_file.write_text("WATLEV OUTPUT 0.0 0.0 0.1 SEC\n")

        # Create empty gauge files
        for i in range(5):
            gauge_file = swash_dir / f"wg{i+1:02d}.txt"
            gauge_file.write_text("0.0 0.0 0.0\n")

        with patch(
            "src.analysis.calculate_wave_statistics_for_gauges"
        ) as mock_wave_stats:
            mock_wave_stats.return_value = pl.DataFrame({"position": [20.0]})

            # Mock plotting to fail (no plot file created)
            with patch("src.analysis._plot_water_levels_and_x_velocities"):
                result = analysis.analyze_simulation(simulation_dir, cfg)

                assert result["plot_file"] == ""


class TestFindTimestep:
    """Test the _find_timestep internal function."""

    def test_find_timestep_success(self, tmp_path: Path) -> None:
        """Test successful timestep extraction."""
        swash_dir = tmp_path / "swash"
        swash_dir.mkdir()
        input_file = swash_dir / "INPUT"
        input_file.write_text(
            "GRID 100.0 200.0 0.0 50.0\n"
            "WATLEV OUTPUT 0.0 0.0 0.1 SEC\n"
            "STOP\n"
        )

        timestep = analysis._find_timestep(tmp_path)
        assert timestep == 0.1

    def test_find_timestep_different_format(self, tmp_path: Path) -> None:
        """Test timestep extraction with different format."""
        swash_dir = tmp_path / "swash"
        swash_dir.mkdir()
        input_file = swash_dir / "INPUT"
        input_file.write_text(
            "WATLEV OUTPUT 0.0 0.0 0.05 SEC\n"
        )

        timestep = analysis._find_timestep(tmp_path)
        assert timestep == 0.05

    def test_find_timestep_file_not_found(self, tmp_path: Path) -> None:
        """Test behavior when INPUT file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            analysis._find_timestep(tmp_path)

    def test_find_timestep_no_watlev_line(self, tmp_path: Path) -> None:
        """Test behavior when WATLEV line is not found."""
        swash_dir = tmp_path / "swash"
        swash_dir.mkdir()
        input_file = swash_dir / "INPUT"
        input_file.write_text("GRID 100.0 200.0 0.0 50.0\nSTOP\n")

        with pytest.raises(UnboundLocalError):
            analysis._find_timestep(tmp_path)

    def test_find_timestep_malformed_watlev_line(self, tmp_path: Path) -> None:
        """Test behavior with malformed WATLEV line."""
        swash_dir = tmp_path / "swash"
        swash_dir.mkdir()
        input_file = swash_dir / "INPUT"
        input_file.write_text("WATLEV OUTPUT\n")

        with pytest.raises(IndexError):
            analysis._find_timestep(tmp_path)


class TestReadSimulationData:
    """Test the _read_simulaton_data internal function."""

    def test_read_simulation_data_success(self, tmp_path: Path) -> None:
        """Test successful data reading."""
        cfg = config.Config(
            name="test",
            numeric=config.NumericConfig(wave_gauge_positions=[20.0, 60.0, 100.0]),
        )
        timestep = 0.1
        
        swash_dir = tmp_path / "swash"
        swash_dir.mkdir()

        # Create test data files
        test_data = np.array([
            [0.1, 0.05, 0.02],
            [0.2, 0.08, 0.03],
            [0.15, 0.06, 0.025]
        ])
        
        for i, position in enumerate(cfg.numeric.wave_gauge_positions):
            gauge_file = swash_dir / f"wg{i+1:02d}.txt"
            np.savetxt(gauge_file, test_data, fmt="%.3f")

        result = analysis._read_simulaton_data(cfg, timestep, tmp_path)

        # Verify structure
        assert isinstance(result, pl.DataFrame)
        expected_columns = {"timestep", "water_level", "x_velocity", "y_velocity", "position"}
        assert set(result.columns) == expected_columns

        # Verify data
        assert len(result) == 9  # 3 gauges × 3 timesteps
        assert result["timestep"].to_list() == [0.0, 0.1, 0.2] * 3
        assert sorted(result["position"].unique().to_list()) == [20.0, 60.0, 100.0]

        # Verify data.csv was created
        assert (swash_dir / "data.csv").exists()

    def test_read_simulation_data_empty_files(self, tmp_path: Path) -> None:
        """Test reading empty gauge files."""
        cfg = config.Config(
            name="test",
            numeric=config.NumericConfig(wave_gauge_positions=[20.0]),
        )
        timestep = 0.1
        
        swash_dir = tmp_path / "swash"
        swash_dir.mkdir()

        # Create empty gauge file
        gauge_file = swash_dir / "wg01.txt"
        gauge_file.write_text("")

        # This should raise an error when trying to read empty CSV
        with pytest.raises(Exception):
            analysis._read_simulaton_data(cfg, timestep, tmp_path)

    def test_read_simulation_data_missing_files(self, tmp_path: Path) -> None:
        """Test behavior when gauge files are missing."""
        cfg = config.Config(
            name="test",
            numeric=config.NumericConfig(wave_gauge_positions=[20.0]),
        )
        timestep = 0.1
        
        swash_dir = tmp_path / "swash"
        swash_dir.mkdir()

        # Don't create any gauge files
        with pytest.raises(FileNotFoundError):
            analysis._read_simulaton_data(cfg, timestep, tmp_path)


class TestPlotWaterLevelsAndXVelocities:
    """Test the _plot_water_levels_and_x_velocities internal function."""

    @pytest.fixture
    def sample_data(self) -> pl.DataFrame:
        """Create sample data for plotting tests."""
        return pl.DataFrame({
            "timestep": [0.0, 0.1, 0.2] * 3,
            "water_level": [0.1, 0.2, 0.15, 0.12, 0.22, 0.16, 0.08, 0.18, 0.13],
            "x_velocity": [0.05, 0.08, 0.06, 0.04, 0.09, 0.07, 0.03, 0.06, 0.05],
            "y_velocity": [0.01, 0.02, 0.015, 0.008, 0.025, 0.018, 0.006, 0.015, 0.012],
            "position": [20.0, 20.0, 20.0, 60.0, 60.0, 60.0, 100.0, 100.0, 100.0],
        })

    def test_plot_with_breakwater_enabled(self, tmp_path: Path, sample_data: pl.DataFrame) -> None:
        """Test plotting with breakwater enabled."""
        cfg = config.Config(
            name="test",
            breakwater=config.BreakwaterConfig(
                enable=True,
                breakwater_start_position=50.0,
                crest_length=10.0,
                crest_height=2.0,
                slope=2.0,
            ),
            numeric=config.NumericConfig(wave_gauge_positions=[20.0, 60.0, 100.0]),
        )
        
        analysis._plot_water_levels_and_x_velocities(sample_data, cfg, 0.1, tmp_path)

        # Verify files were created
        analysis_dir = tmp_path / "analysis"
        assert analysis_dir.exists()
        assert (analysis_dir / "water_levels_and_x_velocity.png").exists()
        assert (analysis_dir / "water_levels_and_x_velocity.json").exists()

        # Verify JSON content has breakwater annotations
        with open(analysis_dir / "water_levels_and_x_velocity.json") as f:
            plot_data = json.load(f)
            
        # Check for breakwater shapes and annotations
        assert "shapes" in plot_data["layout"]
        assert "annotations" in plot_data["layout"]
        assert len(plot_data["layout"]["shapes"]) == 2  # Two rectangles
        assert len(plot_data["layout"]["annotations"]) == 2  # Two annotations

    def test_plot_with_breakwater_disabled(self, tmp_path: Path, sample_data: pl.DataFrame) -> None:
        """Test plotting with breakwater disabled."""
        cfg = config.Config(
            name="test",
            breakwater=config.BreakwaterConfig(enable=False),
            numeric=config.NumericConfig(wave_gauge_positions=[20.0, 60.0, 100.0]),
        )
        
        analysis._plot_water_levels_and_x_velocities(sample_data, cfg, 0.1, tmp_path)

        # Verify files were created
        analysis_dir = tmp_path / "analysis"
        assert analysis_dir.exists()
        assert (analysis_dir / "water_levels_and_x_velocity.png").exists()
        assert (analysis_dir / "water_levels_and_x_velocity.json").exists()

        # Verify JSON content has no breakwater annotations
        with open(analysis_dir / "water_levels_and_x_velocity.json") as f:
            plot_data = json.load(f)
            
        # Check for empty shapes and annotations
        # When breakwater is disabled, these keys should exist but be empty
        assert plot_data["layout"].get("shapes", []) == []
        assert plot_data["layout"].get("annotations", []) == []

    def test_plot_creates_analysis_directory(self, tmp_path: Path, sample_data: pl.DataFrame) -> None:
        """Test that plotting creates analysis directory if it doesn't exist."""
        cfg = config.Config(
            name="test",
            numeric=config.NumericConfig(wave_gauge_positions=[20.0, 60.0, 100.0]),
        )
        
        # Ensure analysis directory doesn't exist
        analysis_dir = tmp_path / "analysis"
        assert not analysis_dir.exists()
        
        analysis._plot_water_levels_and_x_velocities(sample_data, cfg, 0.1, tmp_path)
        
        # Verify directory was created
        assert analysis_dir.exists()

    def test_plot_data_transformation(self, tmp_path: Path, sample_data: pl.DataFrame) -> None:
        """Test that position values are properly transformed to gauge labels."""
        cfg = config.Config(
            name="test",
            numeric=config.NumericConfig(wave_gauge_positions=[20.0, 60.0, 100.0]),
        )
        
        analysis._plot_water_levels_and_x_velocities(sample_data, cfg, 0.1, tmp_path)

        # Verify JSON content has proper gauge labels
        analysis_dir = tmp_path / "analysis"
        with open(analysis_dir / "water_levels_and_x_velocity.json") as f:
            plot_data = json.load(f)
            
        # Check trace data for proper gauge labels
        for trace in plot_data["data"]:
            if "x" in trace:
                # Should contain gauge labels, not raw position values
                x_values = trace["x"]
                assert "Gauge 1 (20.0 m)" in x_values
                assert "Gauge 2 (60.0 m)" in x_values
                assert "Gauge 3 (100.0 m)" in x_values

    def test_position_to_gauge_index_function(self, tmp_path: Path, sample_data: pl.DataFrame) -> None:
        """Test the position_to_gauge_index helper function indirectly."""
        cfg = config.Config(
            name="test",
            breakwater=config.BreakwaterConfig(
                enable=True,
                breakwater_start_position=30.0,  # Between first and second gauge
                crest_length=5.0,
                crest_height=2.0,
                slope=1.0,
            ),
            numeric=config.NumericConfig(wave_gauge_positions=[20.0, 60.0, 100.0]),
        )
        
        analysis._plot_water_levels_and_x_velocities(sample_data, cfg, 0.1, tmp_path)

        # Verify JSON content shows breakwater positioned correctly
        analysis_dir = tmp_path / "analysis"
        with open(analysis_dir / "water_levels_and_x_velocity.json") as f:
            plot_data = json.load(f)
            
        # Check breakwater rectangle positions
        shapes = plot_data["layout"]["shapes"]
        assert len(shapes) == 2
        
        # The start position should be interpolated between gauge indices
        # Position 30.0 is 25% of the way from 20.0 to 60.0, so gauge index should be 0.25
        # End position is 30.0 + 5.0 + 2*(2.0*1.0) = 39.0, which is 47.5% of way, so index 0.475
        first_shape = shapes[0]
        assert first_shape["x0"] == pytest.approx(0.25 - 0.4, abs=0.1)  # start_index - 0.4
        assert first_shape["x1"] == pytest.approx(0.475 + 0.4, abs=0.1)  # end_index + 0.4

    def test_position_to_gauge_index_fallback(self, tmp_path: Path) -> None:
        """Test the fallback case in position_to_gauge_index function."""
        # Import the plotting function to access the nested helper function
        from src.analysis import _plot_water_levels_and_x_velocities
        import types
        
        # Create minimal test data 
        sample_data = pl.DataFrame({
            "timestep": [0.0],
            "water_level": [0.1],
            "x_velocity": [0.05],
            "y_velocity": [0.01],
            "position": [50.0],
        })
        
        # Create a config with non-monotonic gauge positions that will trigger the fallback
        # The specific case: gauges=[20.0, 30.0, 10.0], breakwater at pos=15.0
        # 15.0 > 20.0? NO, 15.0 >= 10.0? YES -> but we need to test the end position too
        cfg = config.Config(
            name="test",
            breakwater=config.BreakwaterConfig(
                enable=True,
                breakwater_start_position=15.0,  # This will trigger fallback
                crest_length=0.1,  # Small length to keep end position at ~15.1
                crest_height=0.1,
                slope=1.0,
            ),
            numeric=config.NumericConfig(wave_gauge_positions=[20.0, 30.0, 10.0]),  # [20, 30, 10] - will trigger fallback for pos=15.0
        )
        
        # This should trigger the fallback case due to non-monotonic gauge positions
        # Position 30.0 won't be found between any consecutive pairs in [100.0, 10.0, 50.0]
        _plot_water_levels_and_x_velocities(sample_data, cfg, 0.1, tmp_path)

        # Verify files were created despite the edge case
        analysis_dir = tmp_path / "analysis"
        assert analysis_dir.exists()
        assert (analysis_dir / "water_levels_and_x_velocity.png").exists()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_wave_gauge_positions(self, tmp_path: Path) -> None:
        """Test behavior with empty wave gauge positions."""
        cfg = config.Config(
            name="test",
            numeric=config.NumericConfig(wave_gauge_positions=[]),
        )
        timestep = 0.1
        
        swash_dir = tmp_path / "swash"
        swash_dir.mkdir()

        # Should raise ValueError due to empty concat list
        with pytest.raises(ValueError, match="cannot concat empty list"):
            analysis._read_simulaton_data(cfg, timestep, tmp_path)

    def test_single_gauge_position(self, tmp_path: Path) -> None:
        """Test with single gauge position."""
        cfg = config.Config(
            name="test",
            numeric=config.NumericConfig(wave_gauge_positions=[50.0]),
        )
        timestep = 0.1
        
        swash_dir = tmp_path / "swash"
        swash_dir.mkdir()

        # Create single gauge file
        test_data = np.array([[0.1, 0.05, 0.02], [0.2, 0.08, 0.03]])
        gauge_file = swash_dir / "wg01.txt"
        np.savetxt(gauge_file, test_data, fmt="%.3f")

        result = analysis._read_simulaton_data(cfg, timestep, tmp_path)
        assert len(result) == 2
        assert result["position"].unique().to_list() == [50.0]

    def test_very_large_timestep(self, tmp_path: Path) -> None:
        """Test with very large timestep values."""
        cfg = config.Config(
            name="test",
            numeric=config.NumericConfig(wave_gauge_positions=[20.0]),
        )
        timestep = 1000.0  # Very large timestep
        
        swash_dir = tmp_path / "swash"
        swash_dir.mkdir()

        test_data = np.array([[0.1, 0.05, 0.02]])
        gauge_file = swash_dir / "wg01.txt"
        np.savetxt(gauge_file, test_data, fmt="%.3f")

        result = analysis._read_simulaton_data(cfg, timestep, tmp_path)
        assert result["timestep"].to_list() == [0.0]  # First timestep is always 0

    def test_extreme_breakwater_positions(self, tmp_path: Path) -> None:
        """Test breakwater positioning at extreme values."""
        sample_data = pl.DataFrame({
            "timestep": [0.0],
            "water_level": [0.1],
            "x_velocity": [0.05],
            "y_velocity": [0.01],
            "position": [50.0],
        })

        # Test breakwater completely before all gauges
        cfg = config.Config(
            name="test",
            breakwater=config.BreakwaterConfig(
                enable=True,
                breakwater_start_position=10.0,
                crest_length=5.0,
                crest_height=1.0,
                slope=1.0,
            ),
            numeric=config.NumericConfig(wave_gauge_positions=[50.0, 100.0]),
        )
        
        # Should not raise an error
        analysis._plot_water_levels_and_x_velocities(sample_data, cfg, 0.1, tmp_path)

        # Test breakwater completely after all gauges
        cfg.breakwater.breakwater_start_position = 200.0
        analysis._plot_water_levels_and_x_velocities(sample_data, cfg, 0.1, tmp_path)

    def test_malformed_gauge_data(self, tmp_path: Path) -> None:
        """Test behavior with malformed gauge data."""
        cfg = config.Config(
            name="test",
            numeric=config.NumericConfig(wave_gauge_positions=[20.0]),
        )
        timestep = 0.1
        
        swash_dir = tmp_path / "swash"
        swash_dir.mkdir()

        # Create gauge file with wrong number of columns
        gauge_file = swash_dir / "wg01.txt"
        gauge_file.write_text("0.1 0.05\n0.2 0.08\n")  # Missing third column

        # pandas handles missing columns by filling with NaN, so this should work
        # but we can check that NaN values are present
        result = analysis._read_simulaton_data(cfg, timestep, tmp_path)
        assert isinstance(result, pl.DataFrame)
        assert len(result) == 2
        
        # Check that y_velocity column contains null values
        assert result["y_velocity"].null_count() == 2

    def test_analyze_simulation_integration_minimal(self, tmp_path: Path) -> None:
        """Integration test with minimal valid setup."""
        cfg = config.Config(
            name="minimal_test",
            breakwater=config.BreakwaterConfig(enable=False),
            vegetation=config.VegetationConfig(enable=False),
            numeric=config.NumericConfig(wave_gauge_positions=[50.0]),
        )

        # Create minimal test setup
        simulation_dir = tmp_path / "test_sim"
        swash_dir = simulation_dir / "swash"
        swash_dir.mkdir(parents=True)

        # Create INPUT file
        input_file = swash_dir / "INPUT"
        input_file.write_text("WATLEV OUTPUT 0.0 0.0 0.1 SEC\n")

        # Create single gauge file
        test_data = np.array([[0.1, 0.05, 0.02]])
        gauge_file = swash_dir / "wg01.txt"
        np.savetxt(gauge_file, test_data, fmt="%.3f")

        # Mock wave statistics
        with patch(
            "src.analysis.calculate_wave_statistics_for_gauges"
        ) as mock_wave_stats:
            mock_wave_stats.return_value = pl.DataFrame({
                "position": [50.0],
                "significant_wave_height": [0.1],
            })

            result = analysis.analyze_simulation(simulation_dir, cfg)

            assert isinstance(result, dict)
            assert "plot_file" in result
            assert "wave_stats" in result
            assert len(result["wave_stats"]) == 1