from pathlib import Path

from .config import Config
from .utils.paths import root_dir

############
# external #
############


def run_simulation(config: Config) -> None:
    template_dir = root_dir / "templates"
    simulation_dir = root_dir / "simulations" / f"{config.name}_{config.hash}"
    simulation_dir.mkdir(parents=True, exist_ok=True)


############
# internal #
############


def _create_barymetry_file(config: Config, *, simulation_dir: Path) -> None:
    pass


def _create_porosity_file(config: Config, *, simulation_dir: Path) -> None:
    pass


def _create_vegetation_file(config: Config, *, simulation_dir: Path) -> None:
    pass


def _create_input_file(
    config: Config, *, simulation_dir: Path, template_dir: Path
) -> None:
    pass
