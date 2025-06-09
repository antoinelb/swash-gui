import subprocess
from pathlib import Path

import numpy as np
from jinja2 import Template

from .analysis import analyze_simulation
from .config import Config
from .utils.paths import root_dir
from .utils.print import done_print, error_print, load_print

############
# external #
############


def run_simulation(config: Config) -> None:
    """Run a SWASH simulation based on the provided configuration.

    Creates the necessary input files (INPUT, bathymetry, porosity, vegetation)
    in the simulation directory and executes SWASH.
    """
    load_print(f"Running simulation {config.name}...")
    template_dir = root_dir / "templates"
    simulation_dir = root_dir / "simulations" / f"{config.name}_{config.hash}"
    swash_dir = simulation_dir / "swash"
    swash_dir.mkdir(parents=True, exist_ok=True)

    # Create all necessary files in swash subdirectory
    _create_bathymetry_file(config, simulation_dir=swash_dir)
    _create_porosity_file(config, simulation_dir=swash_dir)
    _create_structure_height_file(config, simulation_dir=swash_dir)
    if config.vegetation.enable:
        _create_vegetation_file(config, simulation_dir=swash_dir)
    _create_input_file(
        config, simulation_dir=swash_dir, template_dir=template_dir
    )

    # Execute SWASH
    success = _execute_swash(config, simulation_dir=swash_dir)
    
    # Run analysis if simulation succeeded
    if success:
        load_print("Running analysis...")
        try:
            analyze_simulation(config, save_results=True)
            done_print("Analysis completed and saved")
        except Exception as e:
            error_print(f"Analysis failed: {e}")


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
    breakwater_mask = (x >= config.numeric.breakwater_start_position) & (
        x <= config.breakwater_end_position
    )
    structure_height[breakwater_mask] = config.breakwater.crest_height

    # Write to file
    output_path = simulation_dir / "structure_height.txt"
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
    output_path = simulation_dir / "bathymetry.txt"
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
    breakwater_mask = (x >= config.numeric.breakwater_start_position) & (
        x <= config.breakwater_end_position
    )
    porosity[breakwater_mask] = config.breakwater.porosity

    # Write to file
    output_path = simulation_dir / "porosity.txt"
    np.savetxt(output_path, porosity, fmt="%.3f")


def _create_vegetation_file(config: Config, *, simulation_dir: Path) -> None:
    """Create vegetation density file.

    The vegetation file contains the number of plant stems per unit area
    at each grid point. Vegetation is placed only on the breakwater crest
    where the structure height equals the crest height.
    """
    # Create grid points
    x = np.linspace(0, config.grid.length, config.grid.nx_cells + 1)

    # Initialize vegetation density array
    vegetation_density = np.zeros_like(x)

    if config.vegetation.enable:
        # Calculate breakwater geometry to find crest locations
        breakwater_start = config.numeric.breakwater_start_position
        breakwater_end = config.breakwater_end_position
        crest_height = config.breakwater.crest_height
        slope = config.breakwater.slope
        
        # Calculate crest start and end positions
        # Slope distance from base to crest: height * slope
        slope_distance = crest_height * slope
        crest_start = breakwater_start + slope_distance
        crest_end = breakwater_end - slope_distance
        
        # Set vegetation density only on the flat crest area
        crest_mask = (x >= crest_start) & (x <= crest_end)
        vegetation_density[crest_mask] = config.vegetation.plant_density

    # Write to file
    output_path = simulation_dir / "vegetation_density.txt"
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


def _execute_swash(config: Config, *, simulation_dir: Path) -> bool:
    """Execute SWASH simulation and handle errors.

    Runs SWASH in the simulation directory and checks for errors in
    the PRINT and Errfile outputs.
    
    Returns:
        bool: True if simulation succeeded, False otherwise
    """
    load_print("Executing SWASH simulation...")

    # Remove existing error files to get clean error reporting
    errfile_path = simulation_dir / "Errfile"
    if errfile_path.exists():
        errfile_path.unlink()

    try:
        # Run SWASH in the simulation directory
        result = subprocess.run(
            ["swash"],
            cwd=simulation_dir,
            capture_output=True,
            text=True,
            timeout=3600,  # 1 hour timeout
        )

        # Check for errors in output files
        error_msgs = _check_swash_errors(simulation_dir)

        if error_msgs:
            error_print(
                f"SWASH simulation failed with {len(error_msgs)} error(s)"
            )
            for msg in error_msgs:
                error_print(f"  {msg}", indent=2)
            return False

        # Check if SWASH completed successfully
        if result.returncode != 0:
            error_print(f"SWASH exited with code {result.returncode}")
            if result.stderr:
                error_print(f"  {result.stderr.strip()}", indent=2)
            return False

        done_print("SWASH simulation completed successfully")
        return True

    except subprocess.TimeoutExpired:
        error_print("SWASH simulation timed out (1 hour limit)")
        return False
    except FileNotFoundError:
        error_print(
            "SWASH executable not found. Please ensure SWASH is installed and in PATH"
        )
        return False
    except Exception as e:
        error_print(f"Unexpected error running SWASH: {e}")
        return False



def _check_swash_errors(simulation_dir: Path) -> list[str]:
    """Check SWASH output files for errors and return error messages with locations."""
    errors = []

    # Check Errfile
    errfile_path = simulation_dir / "Errfile"
    if errfile_path.exists():
        try:
            with open(errfile_path, "r") as f:
                errfile_content = f.read().strip()
            if errfile_content:
                errors.append(f"Errfile: {errfile_content}")
        except Exception:
            pass

    # Check PRINT file for severe errors and errors
    print_path = simulation_dir / "PRINT"
    if print_path.exists():
        try:
            with open(print_path, "r") as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                line = line.strip()
                if "** Severe error" in line or "** Error" in line:
                    # Extract error message and add line number
                    error_msg = line.replace("**", "").strip()
                    errors.append(f"PRINT line {i}: {error_msg}")

        except Exception:
            pass

    return errors
