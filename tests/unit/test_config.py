from pathlib import Path

import pytest
import ruamel.yaml
from pydantic import ValidationError

from src import config


class TestComputationalGridConfig:
    def test_default_values(self) -> None:
        """Test default values for computational grid config."""
        grid = config.ComputationalGridConfig()
        # Hash is auto-generated, so just check it exists
        assert len(grid.hash) == 8
        assert grid.length == 112.0
        assert grid.nx_cells == 500
        assert grid.n_layers == 2

    def test_hash_generation(self) -> None:
        """Test that hash is automatically generated."""
        grid = config.ComputationalGridConfig()
        assert len(grid.hash) == 8

    def test_properties_are_fixed(self) -> None:
        """Test that properties return fixed values."""
        grid = config.ComputationalGridConfig()
        # Properties should always return the same values
        assert grid.length == 112.0
        assert grid.nx_cells == 500
        assert grid.n_layers == 2


class TestWaterConfig:
    def test_default_values(self) -> None:
        """Test default values for water config."""
        water = config.WaterConfig()
        assert water.water_level == 1.0
        assert water.water_density == 1000.0
        assert water.wave_height == 0.5
        assert water.wave_period == 6.0

    def test_custom_values(self) -> None:
        """Test custom values for water config."""
        water = config.WaterConfig(
            water_level=2.0,
            water_density=1025.0,
            wave_height=1.0,
            wave_period=8.0,
        )
        assert water.water_level == 2.0
        assert water.water_density == 1025.0
        assert water.wave_height == 1.0
        assert water.wave_period == 8.0

    def test_hash_generation(self) -> None:
        """Test that hash is automatically generated."""
        water = config.WaterConfig()
        assert len(water.hash) == 8


class TestBreakwaterConfig:
    def test_default_values(self) -> None:
        """Test default values for breakwater config."""
        breakwater = config.BreakwaterConfig()
        assert breakwater.enable is True
        assert breakwater.crest_height == 2.0
        assert breakwater.crest_length == 2.0
        assert breakwater.slope == 2.0
        assert breakwater.porosity == 0.4
        assert breakwater.stone_density == 2600.0
        assert breakwater.armour_dn50 == 1.150
        assert breakwater.breakwater_start_position == 70.0

    def test_disabled_breakwater(self) -> None:
        """Test disabled breakwater configuration."""
        breakwater = config.BreakwaterConfig(enable=False)
        assert breakwater.enable is False

    def test_custom_values(self) -> None:
        """Test custom values for breakwater config."""
        breakwater = config.BreakwaterConfig(
            crest_height=3.0,
            crest_length=3.0,
            slope=1.5,
            porosity=0.5,
            breakwater_start_position=60.0,
        )
        assert breakwater.crest_height == 3.0
        assert breakwater.crest_length == 3.0
        assert breakwater.slope == 1.5
        assert breakwater.porosity == 0.5
        assert breakwater.breakwater_start_position == 60.0


class TestVegetationType:
    def test_default_values(self) -> None:
        """Test default values for vegetation type."""
        veg_type = config.VegetationType()
        assert veg_type.plant_height == 0.5
        assert veg_type.plant_diameter == 0.01
        assert veg_type.plant_density == 1.0
        assert veg_type.drag_coefficient == 1.0

    def test_custom_values(self) -> None:
        """Test custom values for vegetation type."""
        veg_type = config.VegetationType(
            plant_height=1.0,
            plant_diameter=0.02,
            plant_density=50.0,
            drag_coefficient=1.5,
        )
        assert veg_type.plant_height == 1.0
        assert veg_type.plant_diameter == 0.02
        assert veg_type.plant_density == 50.0
        assert veg_type.drag_coefficient == 1.5


class TestVegetationConfig:
    def test_default_values(self) -> None:
        """Test default values for vegetation config."""
        vegetation = config.VegetationConfig()
        assert vegetation.enable is False
        assert vegetation.type.plant_height == 0.5
        assert vegetation.type.plant_diameter == 0.02
        assert vegetation.type.plant_density == 50.0
        assert vegetation.type.drag_coefficient == 1.2
        assert vegetation.other_type is None
        assert vegetation.distribution == "half"
        assert vegetation.type_fraction == 0.5

    def test_enabled_vegetation(self) -> None:
        """Test enabled vegetation configuration."""
        vegetation = config.VegetationConfig(enable=True)
        assert vegetation.enable is True

    def test_two_vegetation_types(self) -> None:
        """Test configuration with two vegetation types."""
        other_type = config.VegetationType(
            plant_height=0.3,
            plant_diameter=0.01,
            plant_density=100.0,
            drag_coefficient=1.0,
        )
        vegetation = config.VegetationConfig(
            enable=True,
            other_type=other_type,
            distribution="alternating",
            type_fraction=0.7,
        )
        assert vegetation.other_type is not None
        assert vegetation.other_type.plant_height == 0.3
        assert vegetation.distribution == "alternating"
        assert vegetation.type_fraction == 0.7

    def test_type_fraction_validation(self) -> None:
        """Test type_fraction validation (0-1 range)."""
        # Valid values
        config.VegetationConfig(type_fraction=0.0)
        config.VegetationConfig(type_fraction=1.0)
        config.VegetationConfig(type_fraction=0.5)

        # Invalid values
        with pytest.raises(ValidationError):
            config.VegetationConfig(type_fraction=-0.1)
        with pytest.raises(ValidationError):
            config.VegetationConfig(type_fraction=1.1)

    def test_distribution_validation(self) -> None:
        """Test distribution validation (literal values)."""
        # Valid values
        config.VegetationConfig(distribution="half")
        config.VegetationConfig(distribution="alternating")

        # Invalid value
        with pytest.raises(ValidationError):
            config.VegetationConfig(distribution="invalid")  # type: ignore


class TestNumericConfig:
    def test_default_values(self) -> None:
        """Test default values for numeric config."""
        numeric = config.NumericConfig()
        assert numeric.n_waves == 50
        assert numeric.wave_gauge_positions == [20.0, 60.0, 65.0, 80.0, 100.0]
        assert numeric.time_step == 0.05
        assert numeric.output_interval == 0.1

    def test_custom_values(self) -> None:
        """Test custom values for numeric config."""
        numeric = config.NumericConfig(
            n_waves=100,
            wave_gauge_positions=[10.0, 30.0, 50.0, 70.0, 90.0],
        )
        assert numeric.n_waves == 100
        assert numeric.wave_gauge_positions == [10.0, 30.0, 50.0, 70.0, 90.0]

    def test_properties_are_fixed(self) -> None:
        """Test that properties return fixed values."""
        numeric = config.NumericConfig()
        assert numeric.time_step == 0.05
        assert numeric.output_interval == 0.1


class TestConfig:
    def test_default_values(self, minimal_config: config.Config) -> None:
        """Test default values for main config."""
        cfg = config.Config(name="test")
        assert cfg.name == "test"
        assert isinstance(cfg.grid, config.ComputationalGridConfig)
        assert isinstance(cfg.water, config.WaterConfig)
        assert isinstance(cfg.breakwater, config.BreakwaterConfig)
        assert isinstance(cfg.vegetation, config.VegetationConfig)
        assert isinstance(cfg.numeric, config.NumericConfig)

    def test_hash_generation(self) -> None:
        """Test that hash is automatically generated."""
        cfg = config.Config(name="test")
        assert len(cfg.hash) == 8

    def test_simulation_duration(self, full_config: config.Config) -> None:
        """Test simulation duration calculation."""
        # With default values: 50 waves * 6s period = 300s
        cfg = config.Config(name="test")
        assert cfg.simulation_duration == 300.0

        # With custom values
        cfg.numeric.n_waves = 100
        cfg.water.wave_period = 10.0
        assert cfg.simulation_duration == 1000.0

    def test_breakwater_end_position_enabled(self) -> None:
        """Test breakwater end position calculation when enabled."""
        cfg = config.Config(name="test")
        cfg.breakwater.enable = True
        cfg.breakwater.breakwater_start_position = 70.0
        cfg.breakwater.crest_length = 2.0
        cfg.breakwater.crest_height = 2.0
        cfg.breakwater.slope = 2.0

        # end = start + crest_length + 2 * (height * slope)
        # end = 70 + 2 + 2 * (2 * 2) = 70 + 2 + 8 = 80
        assert cfg.breakwater_end_position == 80.0

    def test_breakwater_end_position_disabled(self) -> None:
        """Test breakwater end position when disabled."""
        cfg = config.Config(name="test")
        cfg.breakwater.enable = False
        cfg.breakwater.breakwater_start_position = 70.0

        # When disabled, end position equals start position
        assert cfg.breakwater_end_position == 70.0

    def test_nested_hash_generation(self) -> None:
        """Test that all nested configs have hashes generated."""
        cfg = config.Config(name="test")
        assert len(cfg.hash) == 8
        assert len(cfg.grid.hash) == 8
        assert len(cfg.water.hash) == 8
        assert len(cfg.breakwater.hash) == 8
        assert len(cfg.vegetation.hash) == 8
        assert len(cfg.numeric.hash) == 8


class TestReadConfig:
    def test_read_valid_config(self, config_file: Path) -> None:
        """Test reading a valid config file."""
        cfg = config.read_config(config_file)
        assert cfg.name == "test_minimal"
        assert cfg.water.water_level == 1.0
        assert cfg.water.wave_period == 3.0
        assert cfg.water.wave_height == 0.15
        assert cfg.breakwater.enable is False
        assert cfg.vegetation.enable is False
        assert cfg.numeric.n_waves == 20

    def test_read_config_string_path(self, config_file: Path) -> None:
        """Test reading config with string path."""
        cfg = config.read_config(str(config_file))
        assert cfg.name == "test_minimal"

    def test_read_invalid_yaml(self, tmp_path: Path) -> None:
        """Test reading invalid YAML file."""
        invalid_file = tmp_path / "invalid.yml"
        invalid_file.write_text("invalid: yaml: content:")

        with pytest.raises(Exception):  # YAML parsing error
            config.read_config(invalid_file)

    def test_read_invalid_config_structure(self, tmp_path: Path) -> None:
        """Test reading YAML with invalid config structure."""
        invalid_file = tmp_path / "invalid_structure.yml"
        invalid_file.write_text("water:\n  invalid_field: 123\n")

        # This should succeed because extra fields are allowed by default in Pydantic
        cfg = config.read_config(invalid_file)
        assert cfg.name == "invalid_structure"


class TestWriteConfig:
    def test_write_config(self, full_config: config.Config, tmp_path: Path) -> None:
        """Test writing config to file."""
        output_file = tmp_path / "output.yml"
        config.write_config(full_config, output_file)

        assert output_file.exists()

        # Read back and verify
        yaml = ruamel.yaml.YAML()
        loaded = yaml.load(output_file)

        # Name should be excluded
        assert "name" not in loaded
        assert loaded["water"]["water_level"] == full_config.water.water_level
        assert loaded["breakwater"]["enable"] == full_config.breakwater.enable

    def test_write_config_creates_directories(
        self, full_config: config.Config, tmp_path: Path
    ) -> None:
        """Test that write_config creates parent directories."""
        output_file = tmp_path / "nested" / "dir" / "output.yml"
        config.write_config(full_config, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()

    def test_write_config_with_comments(
        self, full_config: config.Config, tmp_path: Path
    ) -> None:
        """Test that written config includes comments."""
        output_file = tmp_path / "output_with_comments.yml"
        config.write_config(full_config, output_file)

        content = output_file.read_text()
        # Check for some expected comments
        assert "hash of the config" in content
        assert "computational grid configuration" in content
        assert "breakwater configuration" in content


class TestAddComments:
    def test_add_comments(self, full_config: config.Config) -> None:
        """Test _add_comments function."""
        commented = config._add_comments(full_config)

        assert isinstance(commented, ruamel.yaml.CommentedMap)
        assert "hash" in commented
        assert "grid" in commented
        assert "water" in commented
        assert "breakwater" in commented
        assert "vegetation" in commented
        assert "numeric" in commented

        # Check nested structures
        assert isinstance(commented["grid"], ruamel.yaml.CommentedMap)
        assert isinstance(commented["water"], ruamel.yaml.CommentedMap)

    def test_add_field_comments(self) -> None:
        """Test _add_field_comments function."""
        water = config.WaterConfig()
        commented_map = ruamel.yaml.CommentedMap(water.model_dump())

        config._add_field_comments(water, commented_map)

        # The function should have added comments based on field descriptions
        # We can't easily test the actual comments, but we can verify the structure
        assert "water_level" in commented_map
        assert "wave_period" in commented_map