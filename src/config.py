from pathlib import Path

import pydantic
import ruamel.yaml

from src import utils

#########
# types #
#########


class ComputationalGridConfig(pydantic.BaseModel):
    hash: str = pydantic.Field(
        default="",
        description="Hash of the configuration (automatically generated)",
    )

    # domain size
    length: float = pydantic.Field(
        default=112.0, description="Length of the computational domain (m)"
    )

    # grid resolution
    nx_cells: int = pydantic.Field(
        default=500, description="Number of cells in x-direction"
    )

    # vertical layers
    n_layers: int = pydantic.Field(
        default=2,
        description="Number of vertical layers (2-3 recommended for efficiency)",
    )

    _hash_config = utils.validators.hash_config()


class BreakwaterConfig(pydantic.BaseModel):
    hash: str = pydantic.Field(
        default="",
        description="Hash of the configuration (automatically generated)",
    )

    # geometry
    crest_height: float = pydantic.Field(
        default=2.0, description="Height of the crest from the floor (m)"
    )
    crest_width: float = pydantic.Field(
        default=2.0, description="Width of the crest (m)"
    )
    slope: float = pydantic.Field(
        default=2.0, description="Slope of the breakwater sides (H:V ratio)"
    )
    porosity: float = pydantic.Field(
        default=0.4, description="Porosity of the breakwater (0-1)"
    )
    stone_density: float = pydantic.Field(
        default=2600, description="Density of the stones (kg/m^3)"
    )
    armour_dn50: float = pydantic.Field(
        default=1.150, description="Median diameter of armour stones (m)"
    )

    _hash_config = utils.validators.hash_config()


class WaterConfig(pydantic.BaseModel):
    hash: str = pydantic.Field(
        default="",
        description="Hash of the configuration (automatically generated)",
    )

    # water parameters
    water_level: float = pydantic.Field(
        default=1.0, description="Still water level (m)"
    )
    water_density: float = pydantic.Field(
        default=1000, description="Density of water (kg/m^3)"
    )

    # regular wave parameters
    wave_height: float = pydantic.Field(
        default=0.5, description="Wave height for regular waves (m)"
    )
    wave_period: float = pydantic.Field(
        default=6, description="Wave period for regular waves (s)"
    )

    _hash_config = utils.validators.hash_config()


class VegetationConfig(pydantic.BaseModel):
    hash: str = pydantic.Field(
        default="",
        description="Hash of the configuration (automatically generated)",
    )

    enable: bool = pydantic.Field(
        default=False, description="Enable vegetation on the breakwater crest"
    )

    # vegetation characteristics (if enabled)
    plant_height: float = pydantic.Field(
        default=0.5, description="Height of plants (m)"
    )
    plant_diameter: float = pydantic.Field(
        default=0.01, description="Diameter of plant stems (m)"
    )
    plant_density: float = pydantic.Field(
        default=1.0, description="Number of plant stems per square meter"
    )
    drag_coefficient: float = pydantic.Field(
        default=1.0, description="Drag coefficient for vegetation"
    )

    _hash_config = utils.validators.hash_config()


class NumericConfig(pydantic.BaseModel):
    hash: str = pydantic.Field(
        default="",
        description="Hash of the configuration (automatically generated)",
    )

    # simulation parameters
    n_waves: int = pydantic.Field(
        default=50, description="Number of waves to simulate"
    )
    time_step: float = pydantic.Field(
        default=0.05,
        description="Initial time step (s) - adaptive time stepping will adjust this",
    )

    # breakwater position
    breakwater_start_position: float = pydantic.Field(
        default=100.0, description="Start position of the breakwater (m)"
    )

    # gauge positions in x (m)
    wave_gauge_positions: list[float] = pydantic.Field(
        default=[20.0, 60.0, 65.0, 80.0, 100.0],
        description="X-positions of wave gauges (m)",
    )

    # output frequency (s)
    output_interval: float = pydantic.Field(
        default=0.1, description="Time interval for output (s)"
    )

    _hash_config = utils.validators.hash_config()


class Config(pydantic.BaseModel):
    name: str = pydantic.Field(description="Name of the experiment")
    hash: str = pydantic.Field(
        default="",
        description="Hash of the configuration (automatically generated)",
    )

    grid: ComputationalGridConfig = pydantic.Field(
        default_factory=ComputationalGridConfig,
        description="Computational grid configuration",
    )
    breakwater: BreakwaterConfig = pydantic.Field(
        default_factory=BreakwaterConfig,
        description="Breakwater configuration",
    )
    water: WaterConfig = pydantic.Field(
        default_factory=WaterConfig, description="Water and wave configuration"
    )
    vegetation: VegetationConfig = pydantic.Field(
        default_factory=VegetationConfig,
        description="Vegetation configuration",
    )
    numeric: NumericConfig = pydantic.Field(
        default_factory=NumericConfig, description="Numerical parameters"
    )

    _hash_config = utils.validators.hash_config()

    @property
    def simulation_duration(self) -> float:
        """Calculate total simulation duration based on number of waves and period."""
        return self.numeric.n_waves * self.water.wave_period

    @property
    def breakwater_end_position(self) -> float:
        """Calculate breakwater end position based on start position, crest width, and slope."""
        # Total base width = crest width + 2 * (height * slope)
        base_width = self.breakwater.crest_width + 2 * (
            self.breakwater.crest_height * self.breakwater.slope
        )
        return self.numeric.breakwater_start_position + base_width


############
# external #
############


def read_config(path: Path | str) -> Config:
    """
    Reads the config in `path`, converting it and validating it to a Config object.

    Parameters
    ----------
    path : Path | str
        Path with the config written in yaml

    Returns
    -------
    Config
        Config object
    """
    if isinstance(path, str):
        path = Path(path)
    yaml = ruamel.yaml.YAML()
    config = yaml.load(path)
    return Config(name=path.stem, **config)


def write_config(config: Config, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    config_ = _add_comments(config)
    del config_["name"]
    yaml = ruamel.yaml.YAML()
    yaml.dump(config_, path)


############
# internal #
############


def _add_field_comments(config_obj, commented_map: ruamel.yaml.CommentedMap) -> None:
    """Add comments to a CommentedMap based on Pydantic field descriptions."""
    for field_name, field_info in config_obj.__class__.model_fields.items():
        if field_name in commented_map and field_info.description:
            commented_map.yaml_add_eol_comment(field_info.description, field_name)


def _add_comments(config: Config) -> ruamel.yaml.CommentedMap:
    config_ = ruamel.yaml.CommentedMap(config.model_dump())
    
    # Add top-level comments
    config_.yaml_add_eol_comment(
        "hash of the config (automatically modified)", "hash"
    )
    config_.yaml_add_eol_comment("computational grid configuration", "grid")
    config_.yaml_add_eol_comment(
        "configuration for the breakwater", "breakwater"
    )
    config_.yaml_add_eol_comment(
        "configuration for the water in the channel or bay", "water"
    )
    config_.yaml_add_eol_comment(
        "configuration for the vegetation on the breakwater", "vegetation"
    )
    config_.yaml_add_eol_comment(
        "configuration for the numerical parameters",
        "numeric",
    )

    # Add field comments for each section using Pydantic descriptions
    config_["grid"] = ruamel.yaml.CommentedMap(config.grid.model_dump())
    _add_field_comments(config.grid, config_["grid"])
    
    config_["breakwater"] = ruamel.yaml.CommentedMap(config.breakwater.model_dump())
    _add_field_comments(config.breakwater, config_["breakwater"])
    
    config_["water"] = ruamel.yaml.CommentedMap(config.water.model_dump())
    _add_field_comments(config.water, config_["water"])
    
    config_["vegetation"] = ruamel.yaml.CommentedMap(config.vegetation.model_dump())
    _add_field_comments(config.vegetation, config_["vegetation"])
    
    config_["numeric"] = ruamel.yaml.CommentedMap(config.numeric.model_dump())
    _add_field_comments(config.numeric, config_["numeric"])

    return config_


