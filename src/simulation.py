import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional

import numpy as np
import tqdm
from jinja2 import Template

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
    if config.breakwater.enable:
        _create_porosity_file(config, simulation_dir=swash_dir)
        _create_structure_height_file(config, simulation_dir=swash_dir)
        if config.vegetation.enable:
            _create_vegetation_file(config, simulation_dir=swash_dir)
    _create_input_file(
        config, simulation_dir=swash_dir, template_dir=template_dir
    )

    # Execute SWASH
    success = _execute_swash(config, simulation_dir=swash_dir)

    if success:
        done_print("Simulation completed successfully")

        # Run analysis if simulation succeeded
        load_print("Generating wave analysis...")
        try:
            from .analysis import analyze_simulation

            analyze_simulation(simulation_dir, config)
            done_print("Analysis complete - results saved to analysis/")
        except Exception as e:
            error_print(f"Analysis failed: {e}")


############
# internal #
############


def _create_bathymetry_file(config: Config, *, simulation_dir: Path) -> None:
    """Create bathymetry file with flat bottom.

    The bathymetry file contains bottom elevation values at each grid point.
    For a flat bottom, all values are 0.0.
    """
    x = np.linspace(0, config.grid.length, config.grid.nx_cells + 1)
    bottom = np.zeros_like(x)

    output_path = simulation_dir / "bathymetry.txt"
    np.savetxt(output_path, bottom, fmt="%.3f")


def _create_porosity_file(config: Config, *, simulation_dir: Path) -> None:
    """Create porosity file for the breakwater.

    The porosity file contains porosity values at each grid point.
    Porosity is set to the breakwater porosity within the breakwater extent,
    and 0.0 elsewhere.
    """
    x = np.linspace(0, config.grid.length, config.grid.nx_cells + 1)
    porosity = np.ones_like(x)

    breakwater_mask = (x >= config.breakwater.breakwater_start_position) & (
        x <= config.breakwater_end_position
    )
    porosity[breakwater_mask] = config.breakwater.porosity

    output_path = simulation_dir / "porosity.txt"
    np.savetxt(output_path, porosity, fmt="%.3f")


def _create_structure_height_file(
    config: Config, *, simulation_dir: Path
) -> None:
    """Create structure height file for the breakwater.

    The structure height file contains the height of the porous structure
    at each grid point.
    """
    x = np.linspace(0, config.grid.length, config.grid.nx_cells + 1)
    structure_height = np.zeros_like(x)

    breakwater_mask = (x >= config.breakwater.breakwater_start_position) & (
        x <= config.breakwater_end_position
    )
    structure_height[breakwater_mask] = config.breakwater.crest_height

    output_path = simulation_dir / "structure_height.txt"
    np.savetxt(output_path, structure_height, fmt="%.3f")


def _create_vegetation_file(config: Config, *, simulation_dir: Path) -> None:
    """Create vegetation density file for the breakwater crest.

    The vegetation density file contains the number of plant stems per square meter
    at each grid point. Vegetation is only placed on the breakwater crest.
    """
    x = np.linspace(0, config.grid.length, config.grid.nx_cells + 1)
    vegetation_density = np.zeros_like(x)

    # Calculate crest boundaries (top of breakwater)
    crest_start = (
        config.breakwater.breakwater_start_position
        + config.breakwater.crest_height * config.breakwater.slope
    )
    crest_end = crest_start + config.breakwater.crest_length

    # Create mask for crest area
    crest_mask = (x >= crest_start) & (x <= crest_end)

    if config.vegetation.other_type is not None:
        # Two vegetation types with spatial distribution
        if config.vegetation.distribution == "half":
            # Seaward half gets type 1, leeward half gets type 2
            crest_mid = (crest_start + crest_end) / 2
            type1_mask = crest_mask & (x <= crest_mid)
            type2_mask = crest_mask & (x > crest_mid)
            vegetation_density[type1_mask] = (
                config.vegetation.type.plant_density
            )
            vegetation_density[type2_mask] = (
                config.vegetation.other_type.plant_density
            )

        elif config.vegetation.distribution == "alternating":
            # Alternating pattern based on type_fraction
            crest_indices = np.where(crest_mask)[0]
            if len(crest_indices) > 0:
                pattern_length = max(
                    1,
                    int(len(crest_indices) * config.vegetation.type_fraction),
                )
                for i, idx in enumerate(crest_indices):
                    if (i // pattern_length) % 2 == 0:
                        vegetation_density[idx] = (
                            config.vegetation.type.plant_density
                        )
                    else:
                        vegetation_density[idx] = (
                            config.vegetation.other_type.plant_density
                        )

    else:
        # Single vegetation type
        vegetation_density[crest_mask] = config.vegetation.type.plant_density

    output_path = simulation_dir / "vegetation_density.txt"
    np.savetxt(output_path, vegetation_density, fmt="%.3f")


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
    # Generate a short project number from the hash (first 3 chars)
    project_nr = config.hash[:3] if config.hash else "001"

    template_vars = {
        "name": config.name,
        "project_nr": project_nr,
        "grid": config.grid,
        "water": config.water,
        "breakwater": config.breakwater,
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
    """Execute SWASH simulation with progress monitoring.

    Runs SWASH in the simulation directory and shows progress based on
    simulation time advancement.

    Returns:
        bool: True if simulation succeeded, False otherwise
    """
    load_print("Executing SWASH simulation...")

    # Remove existing error files to get clean error reporting
    errfile_path = simulation_dir / "Errfile"
    if errfile_path.exists():
        errfile_path.unlink()

    # Calculate total simulation duration for progress tracking
    total_duration = config.simulation_duration

    try:
        # Start SWASH process with real-time output
        process = subprocess.Popen(
            ["swash"],
            cwd=simulation_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True,
        )

        # Progress tracking variables
        current_time: float = 0.0
        progress_bar: Optional[tqdm.tqdm] = None

        # Monitor SWASH output for progress
        def monitor_progress():
            nonlocal current_time, progress_bar

            # Create progress bar
            progress_bar = tqdm.tqdm(
                total=int(
                    total_duration * 100
                ),  # Use centiseconds for finer resolution
                desc="[*] SWASH Progress",
                unit="cs",
                unit_scale=False,
                bar_format="{l_bar}{bar}| {n}/{total} steps [{elapsed}<{remaining}]",
                leave=False,
                position=0,
                dynamic_ncols=True,
            )

            # Pattern to match SWASH time output
            time_pattern = re.compile(
                r"Time of simulation\s*->\s*(\d+\.\d+)\s*in sec:\s*(\d+\.\d+)"
            )

            print_path = simulation_dir / "PRINT"
            last_position = 0

            while process.poll() is None:
                if print_path.exists():
                    try:
                        with open(print_path, "r") as f:
                            f.seek(last_position)
                            new_content = f.read()
                            last_position = f.tell()

                            # Look for time progress in new content
                            for match in time_pattern.finditer(new_content):
                                sim_time = float(match.group(2))
                                if sim_time > current_time:
                                    current_time = sim_time
                                    # Update progress bar (convert to centiseconds)
                                    if progress_bar is not None:
                                        progress_bar.n = int(
                                            current_time * 100
                                        )
                                        progress_bar.refresh()
                    except (IOError, ValueError):
                        pass

                time.sleep(0.1)  # Check every 100ms

            # Complete the progress bar
            if progress_bar:
                progress_bar.n = progress_bar.total
                progress_bar.refresh()
                progress_bar.close()

        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
        monitor_thread.start()

        # Wait for process to complete
        stdout, stderr = process.communicate(timeout=3600)  # 1 hour timeout

        # Wait for monitoring thread to finish
        monitor_thread.join(timeout=2.0)

        # Ensure progress bar is properly closed and cursor returns to new line
        if progress_bar:
            progress_bar.close()
        print()  # Add newline after progress bar

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
        if process.returncode != 0:
            error_print(f"SWASH exited with code {process.returncode}")
            if stderr:
                error_print(f"  {stderr.strip()}", indent=2)
            return False

        done_print("SWASH simulation completed successfully")
        return True

    except subprocess.TimeoutExpired:
        error_print("SWASH simulation timed out (1 hour limit)")
        if process:
            process.kill()
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
