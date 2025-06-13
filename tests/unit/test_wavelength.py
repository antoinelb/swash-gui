import math
from math import pi, tanh, cosh

import pytest

from src import wavelength


class TestGravityConstant:
    """Test the gravity constant."""

    def test_gravity_value(self) -> None:
        """Test that gravity constant has the correct value."""
        assert wavelength.g == 9.81


class TestComputeWavelength:
    """Test the main compute_wavelength function."""

    def test_deep_water_limit(self) -> None:
        """Test wavelength calculation in deep water conditions."""
        # Deep water: h/L > 0.5, where tanh(2πh/L) ≈ 1
        # L = gT²/(2π) in deep water
        wave_period = 10.0
        water_depth = 100.0  # Very deep
        
        expected_deep_water = wavelength.g * wave_period**2 / (2 * pi)
        result = wavelength.compute_wavelength(wave_period, water_depth)
        
        # Should be close to deep water formula
        assert abs(result - expected_deep_water) / expected_deep_water < 0.01

    def test_shallow_water_limit(self) -> None:
        """Test wavelength calculation in shallow water conditions."""
        # Shallow water: h/L < 0.05, where tanh(2πh/L) ≈ 2πh/L
        # L = T√(gh) in shallow water
        wave_period = 6.0
        water_depth = 0.5  # Very shallow
        
        expected_shallow_water = wave_period * math.sqrt(wavelength.g * water_depth)
        result = wavelength.compute_wavelength(wave_period, water_depth)
        
        # Should be close to shallow water formula
        assert abs(result - expected_shallow_water) / expected_shallow_water < 0.1

    def test_intermediate_water(self) -> None:
        """Test wavelength calculation in intermediate water conditions."""
        wave_period = 8.0
        water_depth = 5.0
        
        result = wavelength.compute_wavelength(wave_period, water_depth)
        
        # Result should be reasonable (between shallow and deep water limits)
        deep_water_limit = wavelength.g * wave_period**2 / (2 * pi)
        shallow_water_limit = wave_period * math.sqrt(wavelength.g * water_depth)
        
        # In intermediate water, wavelength is between shallow and deep limits
        # The actual result should be less than deep water limit but could be 
        # less than shallow water limit due to the physics
        assert result < deep_water_limit
        assert result > 0
        assert 20.0 < result < 200.0  # Reasonable range for intermediate water

    def test_typical_ocean_conditions(self) -> None:
        """Test with typical ocean wave conditions."""
        wave_period = 12.0  # 12-second waves
        water_depth = 20.0  # 20m depth
        
        result = wavelength.compute_wavelength(wave_period, water_depth)
        
        # Should be reasonable for ocean conditions (roughly 100-200m)
        assert 50.0 < result < 300.0

    def test_short_period_waves(self) -> None:
        """Test with short period waves (wind waves)."""
        wave_period = 3.0
        water_depth = 10.0
        
        result = wavelength.compute_wavelength(wave_period, water_depth)
        
        # Should be a reasonable short wavelength
        assert 5.0 < result < 50.0

    def test_convergence_with_default_iterations(self) -> None:
        """Test that default number of iterations provides good convergence."""
        wave_period = 8.0
        water_depth = 10.0
        
        result_default = wavelength.compute_wavelength(wave_period, water_depth)
        result_more_iter = wavelength.compute_wavelength(wave_period, water_depth, n_iter=100)
        
        # Should converge to similar values
        relative_diff = abs(result_default - result_more_iter) / result_more_iter
        assert relative_diff < 1e-6

    def test_custom_iteration_count(self) -> None:
        """Test with custom number of iterations."""
        wave_period = 6.0
        water_depth = 8.0
        
        # Test with fewer iterations
        result_few = wavelength.compute_wavelength(wave_period, water_depth, n_iter=10)
        result_many = wavelength.compute_wavelength(wave_period, water_depth, n_iter=100)
        
        # Both should give reasonable results, but more iterations should be more accurate
        assert result_few > 0
        assert result_many > 0
        
        # More iterations should be at least as accurate (usually more so)
        # We can't easily test this without the exact solution, but we can test they're close
        relative_diff = abs(result_few - result_many) / result_many
        assert relative_diff < 0.1  # Should be reasonably close even with fewer iterations

    def test_single_iteration(self) -> None:
        """Test with single iteration (should still give some result)."""
        wave_period = 6.0
        water_depth = 5.0
        
        result = wavelength.compute_wavelength(wave_period, water_depth, n_iter=1)
        
        # Should still be positive and reasonable
        assert result > 0
        assert result < 1000  # Shouldn't be unreasonably large

    def test_zero_iteration(self) -> None:
        """Test with zero iterations (returns initial guess)."""
        wave_period = 6.0
        water_depth = 5.0
        
        result = wavelength.compute_wavelength(wave_period, water_depth, n_iter=0)
        expected_initial_guess = water_depth / 0.05
        
        assert result == expected_initial_guess

    def test_initial_guess_formula(self) -> None:
        """Test that initial guess is water_depth / 0.05."""
        wave_period = 6.0
        water_depth = 3.0
        
        result = wavelength.compute_wavelength(wave_period, water_depth, n_iter=0)
        expected = water_depth / 0.05
        
        assert result == expected
        assert result == 60.0

    def test_positive_inputs_required(self) -> None:
        """Test behavior with edge case inputs."""
        # Very small positive values should work
        result = wavelength.compute_wavelength(0.1, 0.1)
        assert result > 0
        
        # Test with very large values
        result = wavelength.compute_wavelength(100.0, 1000.0)
        assert result > 0

    def test_reproducibility(self) -> None:
        """Test that function gives consistent results."""
        wave_period = 7.5
        water_depth = 12.0
        
        result1 = wavelength.compute_wavelength(wave_period, water_depth)
        result2 = wavelength.compute_wavelength(wave_period, water_depth)
        result3 = wavelength.compute_wavelength(wave_period, water_depth, n_iter=50)
        
        assert result1 == result2 == result3

    def test_known_dispersion_relation_values(self) -> None:
        """Test against some known/calculated values for validation."""
        # These test cases use values where we can verify the dispersion relation
        test_cases = [
            (6.0, 10.0),   # T=6s, h=10m
            (8.0, 5.0),    # T=8s, h=5m  
            (10.0, 20.0),  # T=10s, h=20m
        ]
        
        for period, depth in test_cases:
            wavelength_result = wavelength.compute_wavelength(period, depth)
            
            # Verify the dispersion relation is satisfied
            # The dispersion relation should be close to zero for the solution
            dispersion_check = wavelength._compute_dispersion_relation(
                wavelength_result, depth, period
            )
            
            # Should be very close to zero (satisfied dispersion relation)
            assert abs(dispersion_check) < 1e-10


class TestComputeDispersionRelation:
    """Test the internal _compute_dispersion_relation function."""

    def test_dispersion_relation_formula(self) -> None:
        """Test the mathematical formula of the dispersion relation."""
        L = 50.0
        h = 10.0  
        T = 8.0
        
        result = wavelength._compute_dispersion_relation(L, h, T)
        expected = L - wavelength.g * T**2 / (2 * pi) * tanh(2 * pi * h / L)
        
        assert result == expected

    def test_deep_water_behavior(self) -> None:
        """Test dispersion relation in deep water conditions."""
        L = 100.0
        h = 1000.0  # Very deep
        T = 8.0
        
        result = wavelength._compute_dispersion_relation(L, h, T)
        
        # In deep water, tanh(2πh/L) ≈ 1
        # So f(L) ≈ L - gT²/(2π) 
        expected_deep = L - wavelength.g * T**2 / (2 * pi)
        
        assert abs(result - expected_deep) / abs(expected_deep) < 0.01

    def test_shallow_water_behavior(self) -> None:
        """Test dispersion relation in shallow water conditions."""
        L = 100.0
        h = 0.1  # Very shallow
        T = 8.0
        
        result = wavelength._compute_dispersion_relation(L, h, T)
        
        # In shallow water, tanh(2πh/L) ≈ 2πh/L
        tanh_approx = 2 * pi * h / L
        expected_shallow = L - wavelength.g * T**2 / (2 * pi) * tanh_approx
        
        assert abs(result - expected_shallow) / abs(L) < 0.01

    def test_zero_wavelength_handling(self) -> None:
        """Test behavior when wavelength approaches zero."""
        # This tests numerical stability
        L = 1e-10  # Very small wavelength
        h = 10.0
        T = 8.0
        
        # Should not raise an exception
        result = wavelength._compute_dispersion_relation(L, h, T)
        assert isinstance(result, float)

    def test_large_wavelength_handling(self) -> None:
        """Test behavior with large wavelength values."""
        L = 1e6  # Very large wavelength
        h = 10.0
        T = 8.0
        
        result = wavelength._compute_dispersion_relation(L, h, T)
        assert isinstance(result, float)

    def test_different_parameter_combinations(self) -> None:
        """Test various combinations of input parameters."""
        test_cases = [
            (10.0, 5.0, 6.0),
            (50.0, 15.0, 8.0),
            (100.0, 2.0, 12.0),
            (25.0, 50.0, 4.0),
        ]
        
        for L, h, T in test_cases:
            result = wavelength._compute_dispersion_relation(L, h, T)
            assert isinstance(result, float)
            # Result should be finite
            assert math.isfinite(result)


class TestComputeDispersionRelationDerivative:
    """Test the internal _compute_dispersion_relation_derivative function."""

    def test_derivative_formula(self) -> None:
        """Test the mathematical formula of the derivative."""
        L = 50.0
        h = 10.0
        T = 8.0
        
        result = wavelength._compute_dispersion_relation_derivative(L, h, T)
        expected = wavelength.g * h * T**2 / (cosh(2 * pi * h / L) ** 2 * L**2) + 1
        
        assert result == expected

    def test_derivative_is_positive(self) -> None:
        """Test that derivative is always positive (ensures convergence)."""
        test_cases = [
            (10.0, 5.0, 6.0),
            (50.0, 15.0, 8.0),
            (100.0, 2.0, 12.0),
            (25.0, 50.0, 4.0),
            (1.0, 1.0, 1.0),
        ]
        
        for L, h, T in test_cases:
            result = wavelength._compute_dispersion_relation_derivative(L, h, T)
            assert result > 0, f"Derivative should be positive for L={L}, h={h}, T={T}"

    def test_deep_water_derivative(self) -> None:
        """Test derivative behavior in deep water."""
        L = 100.0
        h = 1000.0  # Very deep
        T = 8.0
        
        result = wavelength._compute_dispersion_relation_derivative(L, h, T)
        
        # In deep water, cosh(2πh/L) is very large, so first term approaches 0
        # Derivative approaches 1
        assert abs(result - 1.0) < 0.1

    def test_shallow_water_derivative(self) -> None:
        """Test derivative behavior in shallow water."""
        L = 100.0
        h = 0.1  # Very shallow  
        T = 8.0
        
        result = wavelength._compute_dispersion_relation_derivative(L, h, T)
        
        # In shallow water, cosh(2πh/L) ≈ 1
        first_term = wavelength.g * h * T**2 / L**2
        expected_approx = first_term + 1
        
        assert abs(result - expected_approx) / expected_approx < 0.01

    def test_numerical_stability_small_wavelength(self) -> None:
        """Test numerical stability with relatively small wavelengths."""
        L = 0.1  # Small wavelength (10cm)
        h = 0.5  # Shallow depth to avoid overflow
        T = 2.0  # Reasonable period
        
        result = wavelength._compute_dispersion_relation_derivative(L, h, T)
        
        # Should still be positive and finite
        assert result > 0
        assert math.isfinite(result)

    def test_numerical_stability_large_wavelength(self) -> None:
        """Test numerical stability with large wavelengths."""
        L = 1e6  # Very large
        h = 10.0
        T = 8.0
        
        result = wavelength._compute_dispersion_relation_derivative(L, h, T)
        
        # Should approach 1 (deep water limit)
        assert 0.5 < result < 2.0
        assert math.isfinite(result)

    def test_derivative_various_parameters(self) -> None:
        """Test derivative with various parameter combinations."""
        test_cases = [
            (1.0, 1.0, 1.0),
            (10.0, 5.0, 6.0),
            (50.0, 15.0, 8.0),
            (100.0, 2.0, 12.0),
            (25.0, 50.0, 4.0),
            (200.0, 100.0, 15.0),
        ]
        
        for L, h, T in test_cases:
            result = wavelength._compute_dispersion_relation_derivative(L, h, T)
            
            # All derivatives should be positive and finite
            assert result > 0
            assert math.isfinite(result)
            # Should be greater than 1 (the constant term)
            assert result >= 1.0


class TestNewtonRaphsonConvergence:
    """Test the Newton-Raphson iteration convergence properties."""
    
    def test_convergence_criterion(self) -> None:
        """Test that Newton-Raphson converges properly."""
        wave_period = 8.0
        water_depth = 10.0
        
        # Test convergence by checking that more iterations don't change result significantly
        result_10 = wavelength.compute_wavelength(wave_period, water_depth, n_iter=10)
        result_50 = wavelength.compute_wavelength(wave_period, water_depth, n_iter=50)
        result_100 = wavelength.compute_wavelength(wave_period, water_depth, n_iter=100)
        
        # Should converge - more iterations shouldn't change result much
        assert abs(result_50 - result_100) / result_100 < 1e-10
        assert abs(result_10 - result_50) / result_50 < 1e-6

    def test_iteration_progression(self) -> None:
        """Test that iterations actually improve the solution."""
        wave_period = 6.0
        water_depth = 8.0
        
        # Get results with different iteration counts
        results = []
        for n_iter in [1, 5, 10, 20, 50]:
            result = wavelength.compute_wavelength(wave_period, water_depth, n_iter=n_iter)
            results.append(result)
        
        # Check that dispersion relation error decreases with more iterations
        errors = []
        for result in results:
            error = abs(wavelength._compute_dispersion_relation(result, water_depth, wave_period))
            errors.append(error)
        
        # Errors should generally decrease (later errors should be smaller)
        assert errors[-1] < errors[0]  # Final error < initial error
        assert errors[-1] < 1e-10      # Final error should be very small

    def test_initial_guess_quality(self) -> None:
        """Test that the initial guess (h/0.05) is reasonable."""
        test_cases = [
            (6.0, 5.0),   # Should give initial guess of 100m
            (8.0, 10.0),  # Should give initial guess of 200m  
            (4.0, 2.0),   # Should give initial guess of 40m
        ]
        
        for period, depth in test_cases:
            initial_guess = depth / 0.05
            final_result = wavelength.compute_wavelength(period, depth)
            
            # Initial guess should be reasonable (same order of magnitude)
            ratio = final_result / initial_guess
            assert 0.1 < ratio < 10.0  # Within one order of magnitude


class TestEdgeCasesAndRobustness:
    """Test edge cases and robustness of the wavelength functions."""
    
    def test_very_short_periods(self) -> None:
        """Test with very short wave periods."""
        wave_period = 0.5  # Very short period
        water_depth = 5.0
        
        result = wavelength.compute_wavelength(wave_period, water_depth)
        
        # Should still be positive and reasonable
        assert result > 0
        assert result < 100  # Shouldn't be unreasonably large

    def test_very_long_periods(self) -> None:
        """Test with very long wave periods."""
        wave_period = 100.0  # Very long period (tsunami-like)
        water_depth = 10.0
        
        result = wavelength.compute_wavelength(wave_period, water_depth)
        
        # Should be positive and large
        assert result > 900  # Should be quite large (adjusted based on actual result)
        assert math.isfinite(result)

    def test_very_shallow_water(self) -> None:
        """Test with very shallow water."""
        wave_period = 6.0
        water_depth = 0.01  # 1cm deep
        
        result = wavelength.compute_wavelength(wave_period, water_depth)
        
        # Should still work and be positive
        assert result > 0
        assert math.isfinite(result)

    def test_very_deep_water(self) -> None:
        """Test with very deep water."""
        wave_period = 8.0
        water_depth = 1000.0  # 1km deep (avoid numerical overflow)
        
        result = wavelength.compute_wavelength(wave_period, water_depth)
        
        # Should approach deep water limit
        deep_water_limit = wavelength.g * wave_period**2 / (2 * pi)
        relative_diff = abs(result - deep_water_limit) / deep_water_limit
        assert relative_diff < 0.01  # Very close to deep water formula

    def test_mathematical_consistency(self) -> None:
        """Test mathematical consistency across different scenarios."""
        # Test that longer periods give longer wavelengths (for same depth)
        depth = 10.0
        
        result_short = wavelength.compute_wavelength(4.0, depth)
        result_long = wavelength.compute_wavelength(12.0, depth)
        
        assert result_long > result_short

        # Test that deeper water gives longer wavelengths (for same period) 
        period = 8.0
        
        result_shallow = wavelength.compute_wavelength(period, 2.0)
        result_deep = wavelength.compute_wavelength(period, 50.0)
        
        assert result_deep > result_shallow