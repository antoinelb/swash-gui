from pathlib import Path

import pytest

from src import config


@pytest.fixture
def computational_grid_config() -> config.ComputationalGridConfig:
    """Basic computational grid configuration."""
    return config.ComputationalGridConfig()


@pytest.fixture
def water_config() -> config.WaterConfig:
    """Basic water configuration."""
    return config.WaterConfig(
        water_level=1.0,
        water_density=1000.0,
        wave_period=2.5,
        wave_height=0.1,
        wave_angle=0.0,
    )


@pytest.fixture
def breakwater_config() -> config.BreakwaterConfig:
    """Basic breakwater configuration."""
    return config.BreakwaterConfig(
        enable=True,
        position_from_coast=2.0,
        elevation=1.5,
        foot_width=0.5,
        height=1.0,
        crown_width=0.2,
        armor_porosity=0.5,
        stone_diameter_dn50=0.03,
        core_porosity=0.4,
    )


@pytest.fixture
def vegetation_config() -> config.VegetationConfig:
    """Basic vegetation configuration."""
    return config.VegetationConfig(
        enable=True,
        start_position=15.0,
        end_position=30.0,
        plant_height=0.3,
        stem_diameter=0.005,
        plant_density=100.0,
        drag_coefficient=1.0,
    )


@pytest.fixture
def numeric_config() -> config.NumericConfig:
    """Basic numeric configuration."""
    return config.NumericConfig(
        time_step=0.01,
        maximum_cfl=0.5,
        simulation_time=60.0,
        wavemaker_ramp_time=5.0,
        output_interval=1.0,
        include_nonlinear_terms=True,
        include_dispersion=True,
    )


@pytest.fixture
def full_config(
    computational_grid_config: config.ComputationalGridConfig,
    water_config: config.WaterConfig,
    breakwater_config: config.BreakwaterConfig,
    vegetation_config: config.VegetationConfig,
    numeric_config: config.NumericConfig,
) -> config.Config:
    """Full simulation configuration."""
    return config.Config(
        name="test_simulation",
        grid=computational_grid_config,
        water=water_config,
        breakwater=breakwater_config,
        vegetation=vegetation_config,
        numeric=numeric_config,
    )


@pytest.fixture
def minimal_config() -> config.Config:
    """Minimal configuration with breakwater and vegetation disabled."""
    return config.Config(
        name="minimal_test",
        grid=config.ComputationalGridConfig(),
        water=config.WaterConfig(),
        breakwater=config.BreakwaterConfig(enable=False),
        vegetation=config.VegetationConfig(enable=False),
        numeric=config.NumericConfig(simulation_time=30.0),
    )


@pytest.fixture
def test_config_dir(fixtures_dir: Path) -> Path:
    """Directory containing test config files."""
    return fixtures_dir / "config"


@pytest.fixture
def minimal_config_file(test_config_dir: Path) -> Path:
    """Path to minimal test config file."""
    return test_config_dir / "test_minimal.yml"


@pytest.fixture
def full_config_file(test_config_dir: Path) -> Path:
    """Path to full test config file."""
    return test_config_dir / "test_full.yml"


@pytest.fixture
def invalid_config_file(test_config_dir: Path) -> Path:
    """Path to invalid test config file."""
    return test_config_dir / "test_invalid.yml"


@pytest.fixture
def config_file(minimal_config_file: Path) -> Path:
    """Default config file for backward compatibility."""
    return minimal_config_file