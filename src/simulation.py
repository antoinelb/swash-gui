from pathlib import Path

import numpy as np
from jinja2 import Template

from .config import Config
from .utils.paths import root_dir

############
# external #
############


def run_simulation(config: Config) -> None:
    """Run a SWASH simulation based on the provided configuration.

    Creates the necessary input files (INPUT, bathymetry, porosity, vegetation)
    in the simulation directory.
    """
    template_dir = root_dir / "templates"
    simulation_dir = root_dir / "simulations" / f"{config.name}_{config.hash}"
    simulation_dir.mkdir(parents=True, exist_ok=True)

    # Create all necessary files
    _create_bathymetry_file(config, simulation_dir=simulation_dir)
    _create_porosity_file(config, simulation_dir=simulation_dir)
    _create_structure_height_file(config, simulation_dir=simulation_dir)
    if config.vegetation.enable:
        _create_vegetation_file(config, simulation_dir=simulation_dir)
    _create_input_file(
        config, simulation_dir=simulation_dir, template_dir=template_dir
    )


############
# internal #
############


def _create_structure_height_file(
    config: Config, *, simulation_dir: Path
) -> None:
    """Create structure height file for the breakwater.

    The structure height file contains the height of the porous structure
    at each grid point.
    """
    # Create grid points
    x = np.linspace(0, config.grid.length, config.grid.nx_cells + 1)

    # Initialize structure height array
    structure_height = np.zeros_like(x)

    # Set structure height within breakwater extent
    breakwater_mask = (x >= config.breakwater.start_position) & (
        x <= config.breakwater.end_position
    )
    structure_height[breakwater_mask] = config.breakwater.crest_height

    # Write to file
    output_path = simulation_dir / "structure_height.dat"
    np.savetxt(output_path, structure_height, fmt="%.3f")


def _create_bathymetry_file(config: Config, *, simulation_dir: Path) -> None:
    """Create bathymetry file with flat bottom.

    The bathymetry file contains bottom elevation values at each grid point.
    For a flat bottom, all values are 0.0.
    """
    # Create grid points
    x = np.linspace(0, config.grid.length, config.grid.nx_cells + 1)

    # Flat bottom at z=0
    bottom = np.zeros_like(x)

    # Write to file
    output_path = simulation_dir / "bathymetry.dat"
    np.savetxt(output_path, bottom, fmt="%.3f")


def _create_porosity_file(config: Config, *, simulation_dir: Path) -> None:
    """Create porosity file for the breakwater.

    The porosity file contains porosity values at each grid point.
    Porosity is set to the breakwater porosity within the breakwater extent,
    and 0.0 elsewhere.
    """
    # Create grid points
    x = np.linspace(0, config.grid.length, config.grid.nx_cells + 1)

    # Initialize porosity array (0 = no porosity/solid)
    porosity = np.zeros_like(x)

    # Set porosity within breakwater extent
    breakwater_mask = (x >= config.breakwater.start_position) & (
        x <= config.breakwater.end_position
    )
    porosity[breakwater_mask] = config.breakwater.porosity

    # Write to file
    output_path = simulation_dir / "porosity.dat"
    np.savetxt(output_path, porosity, fmt="%.3f")


def _create_vegetation_file(config: Config, *, simulation_dir: Path) -> None:
    """Create vegetation density file.

    The vegetation file contains the number of plant stems per unit area
    at each grid point. Vegetation is placed on the breakwater crest.
    """
    # Create grid points
    x = np.linspace(0, config.grid.length, config.grid.nx_cells + 1)

    # Initialize vegetation density array
    vegetation_density = np.zeros_like(x)

    # Set vegetation density on breakwater crest
    breakwater_mask = (x >= config.breakwater.start_position) & (
        x <= config.breakwater.end_position
    )
    vegetation_density[breakwater_mask] = config.vegetation.plant_density

    # Write to file
    output_path = simulation_dir / "vegetation_density.dat"
    np.savetxt(output_path, vegetation_density, fmt="%.1f")


def _create_input_file(
    config: Config, *, simulation_dir: Path, template_dir: Path
) -> None:
    """Create SWASH INPUT file from template.

    Uses Jinja2 to render the INPUT template with values from the configuration.
    """
    # Load template
    template_path = template_dir / "INPUT"
    with open(template_path, "r") as f:
        template_content = f.read()

    template = Template(template_content)

    # Prepare template variables
    template_vars = {
        "name": config.name,
        "grid": config.grid,
        "breakwater": config.breakwater,
        "water": config.water,
        "vegetation": config.vegetation,
        "numeric": config.numeric,
        "simulation_duration": config.simulation_duration,
        "enumerate": enumerate,  # Make enumerate available in template
    }

    # Render template
    rendered = template.render(**template_vars)

    # Write to file
    output_path = simulation_dir / "INPUT"
    with open(output_path, "w") as f:
        f.write(rendered)
