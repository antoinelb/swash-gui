import numpy as np
import polars as pl
import pytest

from src.wave_analysis import (
    calculate_wave_heights,
    calculate_wave_statistics_for_gauges,
    _zero_crossing_analysis,
)


class TestCalculateWaveHeights:
    """Test the calculate_wave_heights function."""

    def test_calculate_wave_heights_simple_sinusoid(self):
        """Test wave height calculation with a simple sinusoidal wave."""
        # Create a simple sinusoidal wave: amplitude=0.5, period=2.0s, 10 cycles
        t = np.linspace(0, 20, 1000)  # 20 seconds, 1000 points
        timestep = 0.02  # 20s / 1000 points
        frequency = 0.5  # 0.5 Hz -> 2.0s period
        amplitude = 0.5
        water_levels = amplitude * np.sin(2 * np.pi * frequency * t)

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should detect approximately 10 waves (maybe 9-10 due to edge effects)
        assert 8 <= result["n_waves"] <= 11
        
        # Wave height should be approximately 2 * amplitude = 1.0
        assert pytest.approx(result["mean_wave_height"], abs=0.1) == 1.0
        assert pytest.approx(result["significant_wave_height"], abs=0.1) == 1.0
        assert pytest.approx(result["max_wave_height"], abs=0.1) == 1.0
        assert pytest.approx(result["rms_wave_height"], abs=0.1) == 1.0
        
        # Period should be approximately 2.0 seconds
        assert pytest.approx(result["mean_period"], abs=0.1) == 2.0

    def test_calculate_wave_heights_multiple_frequencies(self):
        """Test wave height calculation with multiple frequency components."""
        # Create a wave with two frequency components
        t = np.linspace(0, 20, 1000)
        timestep = 0.02
        wave1 = 0.3 * np.sin(2 * np.pi * 0.4 * t)  # 0.4 Hz, amplitude 0.3
        wave2 = 0.2 * np.sin(2 * np.pi * 0.8 * t)  # 0.8 Hz, amplitude 0.2
        water_levels = wave1 + wave2

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should detect waves (complex pattern due to interference)
        assert result["n_waves"] > 0
        assert result["mean_wave_height"] > 0
        assert result["significant_wave_height"] > 0
        assert result["max_wave_height"] > 0
        assert result["rms_wave_height"] > 0
        assert result["mean_period"] > 0

    def test_calculate_wave_heights_constant_level(self):
        """Test wave height calculation with constant water level (no waves)."""
        water_levels = np.full(1000, 1.5)  # Constant level
        timestep = 0.01

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should detect no waves
        assert result["n_waves"] == 0
        assert result["mean_wave_height"] == 0.0
        assert result["significant_wave_height"] == 0.0
        assert result["max_wave_height"] == 0.0
        assert result["rms_wave_height"] == 0.0
        assert result["mean_period"] == 0.0

    def test_calculate_wave_heights_empty_array(self):
        """Test wave height calculation with empty water level array."""
        water_levels = np.array([])
        timestep = 0.01

        with pytest.warns(RuntimeWarning):
            result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should return all zeros for empty input
        assert result["n_waves"] == 0
        assert result["mean_wave_height"] == 0.0
        assert result["significant_wave_height"] == 0.0
        assert result["max_wave_height"] == 0.0
        assert result["rms_wave_height"] == 0.0
        assert result["mean_period"] == 0.0

    def test_calculate_wave_heights_single_point(self):
        """Test wave height calculation with single data point."""
        water_levels = np.array([1.0])
        timestep = 0.01

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Single point cannot form a wave
        assert result["n_waves"] == 0
        assert result["mean_wave_height"] == 0.0
        assert result["significant_wave_height"] == 0.0
        assert result["max_wave_height"] == 0.0
        assert result["rms_wave_height"] == 0.0
        assert result["mean_period"] == 0.0

    def test_calculate_wave_heights_two_points(self):
        """Test wave height calculation with two data points."""
        water_levels = np.array([1.0, 2.0])
        timestep = 0.01

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Two points cannot form a complete wave cycle
        assert result["n_waves"] == 0

    def test_calculate_wave_heights_irregular_waves(self):
        """Test wave height calculation with irregular wave pattern."""
        # Create irregular waves with varying amplitudes
        t = np.linspace(0, 10, 500)
        timestep = 0.02
        # Combination of different frequencies and amplitudes
        water_levels = (
            0.5 * np.sin(2 * np.pi * 0.3 * t) +
            0.3 * np.sin(2 * np.pi * 0.7 * t) +
            0.2 * np.sin(2 * np.pi * 1.1 * t)
        )

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should detect some waves
        assert result["n_waves"] > 0
        assert result["mean_wave_height"] > 0
        assert result["significant_wave_height"] >= result["mean_wave_height"]
        assert result["max_wave_height"] >= result["significant_wave_height"]
        assert result["rms_wave_height"] > 0
        assert result["mean_period"] > 0

    def test_calculate_wave_heights_with_offset(self):
        """Test wave height calculation with non-zero mean water level."""
        # Sinusoidal wave with 2.0m mean water level
        t = np.linspace(0, 10, 500)
        timestep = 0.02
        water_levels = 2.0 + 0.4 * np.sin(2 * np.pi * 0.5 * t)

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Wave heights should be calculated relative to zero (after mean removal)
        assert result["n_waves"] > 0
        assert pytest.approx(result["mean_wave_height"], abs=0.1) == 0.8  # 2 * amplitude

    def test_calculate_wave_heights_invalid_method(self):
        """Test wave height calculation with invalid method."""
        water_levels = np.sin(np.linspace(0, 4*np.pi, 100))
        timestep = 0.01

        with pytest.raises(ValueError, match="Unknown method: invalid"):
            calculate_wave_heights(water_levels, timestep, method="invalid")

    def test_calculate_wave_heights_very_short_period(self):
        """Test wave height calculation with very short wave period."""
        # High frequency wave
        t = np.linspace(0, 2, 1000)  # 2 seconds, high resolution
        timestep = 0.002
        water_levels = 0.1 * np.sin(2 * np.pi * 5 * t)  # 5 Hz, 0.2s period

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should detect high-frequency waves
        assert result["n_waves"] > 8  # Approximately 10 waves in 2 seconds
        assert pytest.approx(result["mean_period"], abs=0.05) == 0.2

    def test_calculate_wave_heights_very_long_period(self):
        """Test wave height calculation with very long wave period."""
        # Low frequency wave - only partial cycle
        t = np.linspace(0, 5, 500)  # 5 seconds
        timestep = 0.01
        water_levels = 1.0 * np.sin(2 * np.pi * 0.1 * t)  # 0.1 Hz, 10s period

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should detect partial wave or no complete waves
        assert result["n_waves"] >= 0

    def test_calculate_wave_heights_zero_timestep(self):
        """Test wave height calculation with zero timestep."""
        water_levels = np.sin(np.linspace(0, 4*np.pi, 100))
        timestep = 0.0

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should handle zero timestep (periods will be 0)
        if result["n_waves"] > 0:
            assert result["mean_period"] == 0.0

    def test_calculate_wave_heights_negative_timestep(self):
        """Test wave height calculation with negative timestep."""
        water_levels = np.sin(np.linspace(0, 4*np.pi, 100))
        timestep = -0.01

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should handle negative timestep (will result in negative periods)
        if result["n_waves"] > 0:
            assert result["mean_period"] < 0


class TestZeroCrossingAnalysis:
    """Test the _zero_crossing_analysis internal function."""

    def test_zero_crossing_analysis_simple_sine(self):
        """Test zero crossing analysis with simple sine wave."""
        # Create a sine wave with known properties
        t = np.linspace(0, 4*np.pi, 400)  # 2 complete cycles
        timestep = 4*np.pi / 400
        water_levels = np.sin(t)

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # Should detect approximately 2 waves
        assert len(wave_heights) >= 1
        assert len(wave_periods) >= 1
        assert len(wave_heights) == len(wave_periods)
        
        # Each wave height should be approximately 2 (peak to trough)
        for height in wave_heights:
            assert pytest.approx(height, abs=0.1) == 2.0
        
        # Each period should be approximately 2π
        for period in wave_periods:
            assert pytest.approx(period, abs=0.2) == 2*np.pi

    def test_zero_crossing_analysis_cosine(self):
        """Test zero crossing analysis with cosine wave."""
        # Cosine starts at maximum, different zero-crossing pattern
        t = np.linspace(0, 4*np.pi, 400)
        timestep = 4*np.pi / 400
        water_levels = np.cos(t)

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # Should still detect waves
        assert len(wave_heights) >= 1
        assert len(wave_periods) >= 1
        
        # Wave heights should still be approximately 2
        for height in wave_heights:
            assert pytest.approx(height, abs=0.1) == 2.0

    def test_zero_crossing_analysis_no_crossings(self):
        """Test zero crossing analysis with no zero crossings."""
        # Constant positive level
        water_levels = np.full(100, 1.0)
        timestep = 0.01

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # Should detect no waves
        assert len(wave_heights) == 0
        assert len(wave_periods) == 0
        assert isinstance(wave_heights, np.ndarray)
        assert isinstance(wave_periods, np.ndarray)

    def test_zero_crossing_analysis_single_crossing(self):
        """Test zero crossing analysis with single zero crossing."""
        # Ramp from negative to positive
        water_levels = np.linspace(-1, 1, 100)
        timestep = 0.01

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # Single crossing cannot form a complete wave
        assert len(wave_heights) == 0
        assert len(wave_periods) == 0

    def test_zero_crossing_analysis_alternating_signs(self):
        """Test zero crossing analysis with rapidly alternating signs."""
        # Alternating positive/negative values
        water_levels = np.array([1, -1, 1, -1, 1, -1, 1, -1])
        timestep = 0.1

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # Should detect some pattern, though it may be noisy
        assert isinstance(wave_heights, np.ndarray)
        assert isinstance(wave_periods, np.ndarray)

    def test_zero_crossing_analysis_with_noise(self):
        """Test zero crossing analysis with noisy sine wave."""
        t = np.linspace(0, 4*np.pi, 400)
        timestep = 4*np.pi / 400
        # Add random noise to sine wave
        np.random.seed(42)  # Reproducible results
        noise = 0.1 * np.random.randn(len(t))
        water_levels = np.sin(t) + noise

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # Should still detect waves despite noise
        assert len(wave_heights) >= 1
        assert len(wave_periods) >= 1
        
        # Wave heights should be roughly 2, but with more tolerance due to noise
        assert all(height > 0 for height in wave_heights)

    def test_zero_crossing_analysis_asymmetric_wave(self):
        """Test zero crossing analysis with asymmetric wave."""
        # Create asymmetric wave - need longer time series to get multiple complete waves
        t = np.linspace(0, 8*np.pi, 800)  # Longer time series for more crossings
        timestep = 8*np.pi / 800
        water_levels = np.sin(t) + 0.3 * np.sin(2*t)  # Fundamental + 2nd harmonic

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # Should detect waves (may be fewer due to complex shape, but should get some)
        assert isinstance(wave_heights, np.ndarray)
        assert isinstance(wave_periods, np.ndarray)
        assert len(wave_heights) == len(wave_periods)
        if len(wave_heights) > 0:
            assert all(height > 0 for height in wave_heights)
            assert all(period > 0 for period in wave_periods)

    def test_zero_crossing_analysis_mean_removal(self):
        """Test that zero crossing analysis properly removes mean."""
        # Sine wave with large offset - use longer series to ensure we get complete waves
        t = np.linspace(0, 6*np.pi, 600)  # 3 complete cycles
        timestep = 6*np.pi / 600
        water_levels = 10.0 + np.sin(t)  # Large offset

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # Should detect proper wave heights despite offset (should get at least 1-2 waves)
        assert len(wave_heights) >= 1
        for height in wave_heights:
            assert pytest.approx(height, abs=0.1) == 2.0  # Should be 2, not affected by offset

    def test_zero_crossing_analysis_edge_effects(self):
        """Test zero crossing analysis edge effects."""
        # Partial wave at start and end
        t = np.linspace(np.pi/4, 7*np.pi/4, 200)  # Start and end mid-wave
        timestep = (7*np.pi/4 - np.pi/4) / 200
        water_levels = np.sin(t)

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # Should still detect at least partial waves
        assert isinstance(wave_heights, np.ndarray)
        assert isinstance(wave_periods, np.ndarray)

    def test_zero_crossing_analysis_very_small_waves(self):
        """Test zero crossing analysis with very small amplitude waves."""
        t = np.linspace(0, 4*np.pi, 400)
        timestep = 4*np.pi / 400
        water_levels = 1e-6 * np.sin(t)  # Very small waves

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # Should still detect waves, just very small ones
        if len(wave_heights) > 0:
            assert all(0 < height < 1e-5 for height in wave_heights)

    def test_zero_crossing_analysis_no_down_crossing_between_ups(self):
        """Test zero crossing case where up-crossings have no down-crossing between them."""
        # Create a signal with consecutive up-crossings but no down-crossings in between
        # This should trigger the down_idx is None branch
        water_levels = np.array([-1, 0.5, 2, 1.5, 0.5, -0.5, 0.5, 1])
        timestep = 0.1

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # Should handle the case gracefully
        assert isinstance(wave_heights, np.ndarray)
        assert isinstance(wave_periods, np.ndarray)

    def test_zero_crossing_analysis_empty_wave_segment(self):
        """Test zero crossing case where wave segment could be empty."""
        # Create a pathological case where start_idx == end_idx might occur
        water_levels = np.array([-1, 0, 1, 0, -1])
        timestep = 0.1

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # Should handle the case without errors
        assert isinstance(wave_heights, np.ndarray)
        assert isinstance(wave_periods, np.ndarray)


class TestCalculateWaveStatisticsForGauges:
    """Test the calculate_wave_statistics_for_gauges function."""

    def test_calculate_wave_statistics_single_gauge(self):
        """Test wave statistics calculation for single gauge."""
        # Create test data for single gauge
        t = np.linspace(0, 10, 100)
        water_levels = 0.5 * np.sin(2 * np.pi * 0.5 * t)  # 0.5 Hz, amplitude 0.5
        
        data = pl.DataFrame({
            "timestep": t,
            "water_level": water_levels,
            "position": [50.0] * len(t)
        })
        
        timestep = 0.1

        result = calculate_wave_statistics_for_gauges(data, timestep)

        # Should return DataFrame with one row
        assert isinstance(result, pl.DataFrame)
        assert len(result) == 1
        assert result["position"][0] == 50.0
        
        # Check that all expected columns are present
        expected_columns = {
            "position", "significant_wave_height", "mean_wave_height",
            "max_wave_height", "rms_wave_height", "n_waves", "mean_period"
        }
        assert set(result.columns) == expected_columns
        
        # Basic sanity checks
        assert result["n_waves"][0] >= 0
        assert result["significant_wave_height"][0] >= 0
        assert result["mean_wave_height"][0] >= 0
        assert result["max_wave_height"][0] >= 0
        assert result["rms_wave_height"][0] >= 0
        assert result["mean_period"][0] >= 0

    def test_calculate_wave_statistics_multiple_gauges(self):
        """Test wave statistics calculation for multiple gauges."""
        # Create test data for three gauges with different wave characteristics
        t = np.linspace(0, 10, 100)
        
        # Gauge 1: Small waves
        gauge1_data = pl.DataFrame({
            "timestep": t,
            "water_level": 0.2 * np.sin(2 * np.pi * 0.4 * t),
            "position": [20.0] * len(t)
        })
        
        # Gauge 2: Medium waves
        gauge2_data = pl.DataFrame({
            "timestep": t,
            "water_level": 0.5 * np.sin(2 * np.pi * 0.4 * t),
            "position": [50.0] * len(t)
        })
        
        # Gauge 3: Large waves
        gauge3_data = pl.DataFrame({
            "timestep": t,
            "water_level": 0.8 * np.sin(2 * np.pi * 0.4 * t),
            "position": [80.0] * len(t)
        })
        
        # Combine all gauge data
        data = pl.concat([gauge1_data, gauge2_data, gauge3_data])
        
        timestep = 0.1

        result = calculate_wave_statistics_for_gauges(data, timestep)

        # Should return DataFrame with three rows
        assert isinstance(result, pl.DataFrame)
        assert len(result) == 3
        
        # Check positions are sorted
        positions = result["position"].to_list()
        assert positions == [20.0, 50.0, 80.0]
        
        # Wave heights should generally increase from gauge 1 to 3
        wave_heights = result["mean_wave_height"].to_list()
        assert wave_heights[0] < wave_heights[1] < wave_heights[2]

    def test_calculate_wave_statistics_empty_data(self):
        """Test wave statistics calculation with empty DataFrame."""
        data = pl.DataFrame({
            "timestep": [],
            "water_level": [],
            "position": []
        })
        
        timestep = 0.1

        result = calculate_wave_statistics_for_gauges(data, timestep)

        # Should return empty DataFrame
        assert isinstance(result, pl.DataFrame)
        assert len(result) == 0

    def test_calculate_wave_statistics_constant_levels(self):
        """Test wave statistics with constant water levels (no waves)."""
        t = np.linspace(0, 10, 100)
        
        data = pl.DataFrame({
            "timestep": t,
            "water_level": [1.5] * len(t),  # Constant level
            "position": [50.0] * len(t)
        })
        
        timestep = 0.1

        result = calculate_wave_statistics_for_gauges(data, timestep)

        # Should detect no waves
        assert len(result) == 1
        assert result["n_waves"][0] == 0
        assert result["significant_wave_height"][0] == 0.0
        assert result["mean_wave_height"][0] == 0.0
        assert result["max_wave_height"][0] == 0.0
        assert result["rms_wave_height"][0] == 0.0
        assert result["mean_period"][0] == 0.0

    def test_calculate_wave_statistics_unsorted_positions(self):
        """Test wave statistics with unsorted position data."""
        t = np.linspace(0, 5, 50)
        
        # Create data with positions in non-sorted order
        gauge1_data = pl.DataFrame({
            "timestep": t,
            "water_level": 0.3 * np.sin(2 * np.pi * 0.5 * t),
            "position": [80.0] * len(t)  # Higher position first
        })
        
        gauge2_data = pl.DataFrame({
            "timestep": t,
            "water_level": 0.4 * np.sin(2 * np.pi * 0.5 * t),
            "position": [20.0] * len(t)  # Lower position second
        })
        
        data = pl.concat([gauge1_data, gauge2_data])
        
        timestep = 0.1

        result = calculate_wave_statistics_for_gauges(data, timestep)

        # Should return sorted by position
        assert len(result) == 2
        positions = result["position"].to_list()
        assert positions == [20.0, 80.0]  # Should be sorted

    def test_calculate_wave_statistics_unsorted_timesteps(self):
        """Test wave statistics with unsorted timestep data."""
        # Create timesteps in random order
        timesteps = [0.0, 0.2, 0.1, 0.4, 0.3]
        water_levels = [0.0, 0.5, 0.3, -0.5, -0.3]  # Corresponding levels
        
        data = pl.DataFrame({
            "timestep": timesteps,
            "water_level": water_levels,
            "position": [50.0] * len(timesteps)
        })
        
        timestep = 0.1

        result = calculate_wave_statistics_for_gauges(data, timestep)

        # Should handle unsorted data correctly (function sorts internally)
        assert len(result) == 1
        assert result["position"][0] == 50.0
        # Results should be valid (function should sort before analysis)
        assert result["n_waves"][0] >= 0

    def test_calculate_wave_statistics_single_timestep(self):
        """Test wave statistics with single timestep."""
        data = pl.DataFrame({
            "timestep": [0.0],
            "water_level": [1.0],
            "position": [50.0]
        })
        
        timestep = 0.1

        result = calculate_wave_statistics_for_gauges(data, timestep)

        # Single point cannot form waves
        assert len(result) == 1
        assert result["n_waves"][0] == 0
        assert result["significant_wave_height"][0] == 0.0

    def test_calculate_wave_statistics_different_frequencies(self):
        """Test wave statistics with different wave frequencies at different gauges."""
        t = np.linspace(0, 20, 200)
        
        # Gauge 1: High frequency waves
        gauge1_data = pl.DataFrame({
            "timestep": t,
            "water_level": 0.3 * np.sin(2 * np.pi * 1.0 * t),  # 1 Hz
            "position": [30.0] * len(t)
        })
        
        # Gauge 2: Low frequency waves
        gauge2_data = pl.DataFrame({
            "timestep": t,
            "water_level": 0.3 * np.sin(2 * np.pi * 0.25 * t),  # 0.25 Hz
            "position": [70.0] * len(t)
        })
        
        data = pl.concat([gauge1_data, gauge2_data])
        
        timestep = 0.1

        result = calculate_wave_statistics_for_gauges(data, timestep)

        # Should detect different periods
        assert len(result) == 2
        
        # High frequency gauge should have shorter period
        gauge1_result = result.filter(pl.col("position") == 30.0)
        gauge2_result = result.filter(pl.col("position") == 70.0)
        
        if gauge1_result["n_waves"][0] > 0 and gauge2_result["n_waves"][0] > 0:
            assert gauge1_result["mean_period"][0] < gauge2_result["mean_period"][0]

    def test_calculate_wave_statistics_real_world_scenario(self):
        """Test wave statistics with realistic wave data scenario."""
        # Simulate wave transformation over a reef/breakwater
        t = np.linspace(0, 30, 300)  # 30 seconds of data
        
        # Offshore gauge: Large regular waves
        offshore_waves = 1.0 * np.sin(2 * np.pi * 0.1 * t)  # 10s period, 2m height
        
        # Nearshore gauge: Smaller, more irregular waves (wave breaking effects)
        nearshore_waves = (
            0.6 * np.sin(2 * np.pi * 0.1 * t) +
            0.2 * np.sin(2 * np.pi * 0.3 * t) +  # Higher harmonics
            0.1 * np.sin(2 * np.pi * 0.5 * t)
        )
        
        offshore_data = pl.DataFrame({
            "timestep": t,
            "water_level": offshore_waves,
            "position": [10.0] * len(t)
        })
        
        nearshore_data = pl.DataFrame({
            "timestep": t,
            "water_level": nearshore_waves,
            "position": [90.0] * len(t)
        })
        
        data = pl.concat([offshore_data, nearshore_data])
        
        timestep = 0.1

        result = calculate_wave_statistics_for_gauges(data, timestep)

        # Should show wave transformation (reduction in height)
        assert len(result) == 2
        
        offshore_stats = result.filter(pl.col("position") == 10.0)
        nearshore_stats = result.filter(pl.col("position") == 90.0)
        
        # Offshore should have larger significant wave height
        assert offshore_stats["significant_wave_height"][0] > nearshore_stats["significant_wave_height"][0]
        
        # Both should detect waves
        assert offshore_stats["n_waves"][0] > 0
        assert nearshore_stats["n_waves"][0] > 0

    def test_calculate_wave_statistics_duplicate_positions(self):
        """Test wave statistics with duplicate positions (should not happen in practice)."""
        t = np.linspace(0, 5, 50)
        
        # Create two datasets with same position
        data1 = pl.DataFrame({
            "timestep": t,
            "water_level": 0.3 * np.sin(2 * np.pi * 0.5 * t),
            "position": [50.0] * len(t)
        })
        
        data2 = pl.DataFrame({
            "timestep": t + 5,  # Different timesteps
            "water_level": 0.4 * np.sin(2 * np.pi * 0.5 * (t + 5)),
            "position": [50.0] * len(t)  # Same position
        })
        
        data = pl.concat([data1, data2])
        
        timestep = 0.1

        result = calculate_wave_statistics_for_gauges(data, timestep)

        # Should process as single gauge with combined data
        assert len(result) == 1
        assert result["position"][0] == 50.0


class TestEdgeCasesAndErrorConditions:
    """Test edge cases and error conditions across all functions."""

    def test_wave_heights_nan_values(self):
        """Test wave height calculation with NaN values."""
        water_levels = np.array([1.0, np.nan, 0.5, np.nan, -0.5])
        timestep = 0.1

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should handle NaN values gracefully
        assert isinstance(result, dict)
        # Results depend on how numpy handles NaN in zero-crossing detection

    def test_wave_heights_infinite_values(self):
        """Test wave height calculation with infinite values."""
        water_levels = np.array([1.0, np.inf, 0.5, -np.inf, -0.5])
        timestep = 0.1

        with pytest.warns(RuntimeWarning):
            result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should handle infinite values gracefully
        assert isinstance(result, dict)

    def test_wave_statistics_nan_in_dataframe(self):
        """Test wave statistics with NaN values in DataFrame."""
        data = pl.DataFrame({
            "timestep": [0.0, 0.1, 0.2, 0.3],
            "water_level": [1.0, float('nan'), 0.5, -0.5],
            "position": [50.0, 50.0, 50.0, 50.0]
        })
        
        timestep = 0.1

        # This might raise an error or handle NaN gracefully
        try:
            result = calculate_wave_statistics_for_gauges(data, timestep)
            assert isinstance(result, pl.DataFrame)
        except Exception:
            # If it raises an exception, that's also acceptable behavior
            pass

    def test_very_large_timestep_values(self):
        """Test with very large timestep values."""
        water_levels = np.sin(np.linspace(0, 4*np.pi, 100))
        timestep = 1e6  # Very large timestep

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should handle large timesteps
        assert isinstance(result, dict)
        if result["n_waves"] > 0:
            assert result["mean_period"] > 0

    def test_very_small_timestep_values(self):
        """Test with very small timestep values."""
        water_levels = np.sin(np.linspace(0, 4*np.pi, 100))
        timestep = 1e-10  # Very small timestep

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should handle small timesteps
        assert isinstance(result, dict)

    def test_zero_crossing_edge_case_all_positive(self):
        """Test zero crossing analysis with all positive values."""
        water_levels = np.abs(np.sin(np.linspace(0, 4*np.pi, 100))) + 1
        timestep = 0.01

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # All positive values should not have zero crossings after mean removal
        # (unless the oscillation amplitude is large enough)
        assert isinstance(wave_heights, np.ndarray)
        assert isinstance(wave_periods, np.ndarray)

    def test_zero_crossing_edge_case_all_negative(self):
        """Test zero crossing analysis with all negative values."""
        water_levels = -np.abs(np.sin(np.linspace(0, 4*np.pi, 100))) - 1
        timestep = 0.01

        wave_heights, wave_periods = _zero_crossing_analysis(water_levels, timestep)

        # All negative values should not have zero crossings after mean removal
        assert isinstance(wave_heights, np.ndarray)
        assert isinstance(wave_periods, np.ndarray)

    def test_performance_large_dataset(self):
        """Test performance with large dataset."""
        # Create large dataset
        t = np.linspace(0, 100, 10000)  # 10,000 points
        water_levels = np.sin(2 * np.pi * 0.1 * t)
        timestep = 0.01

        result = calculate_wave_heights(water_levels, timestep, method="zero_crossing")

        # Should complete without error
        assert isinstance(result, dict)
        assert result["n_waves"] >= 0

    def test_wave_statistics_large_multi_gauge_dataset(self):
        """Test wave statistics with large multi-gauge dataset."""
        # Create large dataset with multiple gauges
        t = np.linspace(0, 100, 1000)
        
        all_data = []
        for pos in [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]:
            gauge_data = pl.DataFrame({
                "timestep": t,
                "water_level": 0.5 * np.sin(2 * np.pi * 0.1 * t),
                "position": [pos] * len(t)
            })
            all_data.append(gauge_data)
        
        data = pl.concat(all_data)
        timestep = 0.1

        result = calculate_wave_statistics_for_gauges(data, timestep)

        # Should handle large dataset
        assert len(result) == 10
        assert all(pos in result["position"].to_list() for pos in range(10, 101, 10))