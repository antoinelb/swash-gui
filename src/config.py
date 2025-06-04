from pathlib import Path

import pydantic
import ruamel.yaml

from src import utils

#########
# types #
#########


class ComputationalGridConfig(pydantic.BaseModel):
    hash: str = ""

    # domain size
    length: float = 112.0  # xlenc (m)

    # grid resolution
    nx_cells: int = 500  # mxc (number of cells in x)

    # vertical layers
    n_layers: int = 2  # kmax

    _hash_config = utils.validators.hash_config()


class BreakwaterConfig(pydantic.BaseModel):
    hash: str = ""

    # position
    start_position: float = 100.0
    end_position: float = 200.0

    # geometry
    crest_height: float = 2.0
    crest_width: float = 2.0
    porosity: float = 0.4
    stone_density: float = 2600
    armour_dn50: float = 1.150
    filter_dn50: float = 0.5
    core_dn50: float = 0.2

    _hash_config = utils.validators.hash_config()


class WaterConfig(pydantic.BaseModel):
    hash: str = ""

    # water parameters
    water_level: float = 1.0
    water_density: float = 1000

    # regular wave parameters
    wave_height: float = 0.5
    wave_period: float = 6

    _hash_config = utils.validators.hash_config()


class VegetationConfig(pydantic.BaseModel):
    hash: str = ""

    enable: bool = False

    # vegetation characteristics (if enabled)
    plant_height: float = 0.5  # m
    plant_diameter: float = 0.01  # m
    plant_density: float = 100  # stems per m²
    drag_coefficient: float = 1.0  # Cd

    _hash_config = utils.validators.hash_config()


class NumericConfig(pydantic.BaseModel):
    hash: str = ""

    # simulation parameters
    n_waves: int = 50
    time_step: float = 0.05

    # gauge positions in x (m)
    wave_gauge_positions: list[float] = [20.0, 60.0, 65.0, 80.0, 100.0]

    # output frequency (s)
    output_interval: float = 0.1

    _hash_config = utils.validators.hash_config()


class Config(pydantic.BaseModel):
    name: str
    hash: str = ""

    breakwater: BreakwaterConfig = BreakwaterConfig()
    water: WaterConfig = WaterConfig()
    vegetation: VegetationConfig = VegetationConfig()
    numeric: NumericConfig = NumericConfig()

    _hash_config = utils.validators.hash_config()


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
    config_.yaml_add_eol_comment("name of the experiment", "experiment")
    config_.yaml_add_eol_comment(
        "hash of the config (automatically modified)", "hash"
    )
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
        "configuration for the other numerical parameters",
        "numeric",
    )
    config_.yaml_add_eol_comment(
        "configuration for the other numerical parameters",
        "output",
    )

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


def _add_water_comments(config: WaterConfig) -> ruamel.yaml.CommentedMap:
    config_ = ruamel.yaml.CommentedMap(config.model_dump())
    config_.yaml_add_eol_comment(
        "hash of the config (automatically modified)", "hash"
    )
    config_.yaml_add_eol_comment(
        "height of the still water (m)", "water_level"
    )
    config_.yaml_add_eol_comment("height of the waves (m)", "wave_height")
    config_.yaml_add_eol_comment("period of each wave (s)", "wave_period")
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
        "if there is generation on the crest", "enable"
    )
    return config_


def _add_numeric_comments(config: NumericConfig) -> ruamel.yaml.CommentedMap:
    config_ = ruamel.yaml.CommentedMap(config.model_dump())
    config_.yaml_add_eol_comment(
        "hash of the config (automatically modified)", "hash"
    )
    config_.yaml_add_eol_comment(
        "number of waves during the simulation (-)", "n_waves"
    )
    config_.yaml_add_eol_comment("length of the channel or bay (m)", "length")
    return config_
