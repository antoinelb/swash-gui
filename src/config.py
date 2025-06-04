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

    # position
    start_position: float = pydantic.Field(
        default=100.0, description="Start position of the breakwater (m)"
    )
    end_position: float = pydantic.Field(
        default=102.0, description="End position of the breakwater (m)"
    )

    # geometry
    crest_height: float = pydantic.Field(
        default=2.0, description="Height of the crest from the floor (m)"
    )
    crest_width: float = pydantic.Field(
        default=2.0, description="Width of the crest (m)"
    )
    porosity: float = pydantic.Field(
        default=0.4, description="Porosity of the breakwater (0-1)"
    )
    stone_density: float = pydantic.Field(
        default=2600, description="Density of the stones (kg/m³)"
    )
    armour_dn50: float = pydantic.Field(
        default=1.150, description="Median diameter of the armour stones (m)"
    )
    filter_dn50: float = pydantic.Field(
        default=0.5, description="Median diameter of the filter stones (m)"
    )
    core_dn50: float = pydantic.Field(
        default=0.2, description="Median diameter of the core stones (m)"
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
        default=1000, description="Density of water (kg/m³)"
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
        default=100, description="Number of plant stems per square meter"
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


def save_config(config: Config, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    config_ = _add_comments(config)
    del config_["name"]
    yaml = ruamel.yaml.YAML()
    yaml.dump(config_, path)


############
# internal #
############


def _add_comments(config: Config) -> ruamel.yaml.CommentedMap:
    config_ = ruamel.yaml.CommentedMap(config.model_dump())
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

    config_["grid"] = _add_grid_comments(config.grid)
    config_["breakwater"] = _add_breakwater_comments(config.breakwater)
    config_["vegetation"] = _add_vegetation_comments(config.vegetation)
    config_["water"] = _add_water_comments(config.water)
    config_["numeric"] = _add_numeric_comments(config.numeric)

    return config_


def _add_breakwater_comments(
    config: BreakwaterConfig,
) -> ruamel.yaml.CommentedMap:
    config_ = ruamel.yaml.CommentedMap(config.model_dump())
    config_.yaml_add_eol_comment(
        "hash of the config (automatically modified)", "hash"
    )
    config_.yaml_add_eol_comment(
        "height of the crest from the floor (m)", "crest_height"
    )
    config_.yaml_add_eol_comment("crest width (m)", "crest_width")
    config_.yaml_add_eol_comment("porosity of the breakwater (-)", "porosity")
    config_.yaml_add_eol_comment(
        "density of the stones (kg/m³)", "stone_density"
    )
    config_.yaml_add_eol_comment(
        "median diameter of the armour stones (m)", "armour_dn50"
    )
    config_.yaml_add_eol_comment(
        "median diameter of the filter stones (m)", "filter_dn50"
    )
    config_.yaml_add_eol_comment(
        "median diameter of the core stones (m)", "core_dn50"
    )
    config_.yaml_add_eol_comment(
        "position of the start of the breakwater (m)", "start_position"
    )
    config_.yaml_add_eol_comment(
        "position of the end of the breakwater (m)", "end_position"
    )
    return config_


def _add_grid_comments(
    config: ComputationalGridConfig,
) -> ruamel.yaml.CommentedMap:
    config_ = ruamel.yaml.CommentedMap(config.model_dump())
    config_.yaml_add_eol_comment(
        "hash of the config (automatically modified)", "hash"
    )
    config_.yaml_add_eol_comment(
        "length of the computational domain (m)", "length"
    )
    config_.yaml_add_eol_comment("number of cells in x-direction", "nx_cells")
    config_.yaml_add_eol_comment(
        "number of vertical layers (2-3 recommended)", "n_layers"
    )
    return config_


def _add_water_comments(config: WaterConfig) -> ruamel.yaml.CommentedMap:
    config_ = ruamel.yaml.CommentedMap(config.model_dump())
    config_.yaml_add_eol_comment(
        "hash of the config (automatically modified)", "hash"
    )
    config_.yaml_add_eol_comment("still water level (m)", "water_level")
    config_.yaml_add_eol_comment(
        "wave height for regular waves (m)", "wave_height"
    )
    config_.yaml_add_eol_comment(
        "wave period for regular waves (s)", "wave_period"
    )
    config_.yaml_add_eol_comment(
        "density of the water (kg/m³)", "water_density"
    )
    return config_


def _add_vegetation_comments(
    config: VegetationConfig,
) -> ruamel.yaml.CommentedMap:
    config_ = ruamel.yaml.CommentedMap(config.model_dump())
    config_.yaml_add_eol_comment(
        "hash of the config (automatically modified)", "hash"
    )
    config_.yaml_add_eol_comment(
        "enable vegetation on the breakwater crest", "enable"
    )
    config_.yaml_add_eol_comment("height of plants (m)", "plant_height")
    config_.yaml_add_eol_comment(
        "diameter of plant stems (m)", "plant_diameter"
    )
    config_.yaml_add_eol_comment(
        "number of plant stems per square meter", "plant_density"
    )
    config_.yaml_add_eol_comment(
        "drag coefficient for vegetation", "drag_coefficient"
    )
    return config_


def _add_numeric_comments(config: NumericConfig) -> ruamel.yaml.CommentedMap:
    config_ = ruamel.yaml.CommentedMap(config.model_dump())
    config_.yaml_add_eol_comment(
        "hash of the config (automatically modified)", "hash"
    )
    config_.yaml_add_eol_comment("number of waves to simulate", "n_waves")
    config_.yaml_add_eol_comment(
        "initial time step (s) - adaptive time stepping will adjust",
        "time_step",
    )
    config_.yaml_add_eol_comment(
        "x-positions of wave gauges (m)", "wave_gauge_positions"
    )
    config_.yaml_add_eol_comment(
        "time interval for output (s)", "output_interval"
    )
    return config_
