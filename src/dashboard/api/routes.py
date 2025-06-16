import traceback
from pathlib import Path
from typing import List

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from src import config as config_module
from src.simulation import run_simulation
from src.utils.paths import root_dir
from src.wavelength import compute_wavelength

CONFIG_DIR = Path("config")


async def list_configs(request: Request) -> JSONResponse:
    """List all available configurations."""
    if not CONFIG_DIR.exists():
        return JSONResponse({"configs": []})

    configs = []
    for yaml_file in CONFIG_DIR.glob("*.yml"):
        try:
            cfg = config_module.read_config(yaml_file)
            configs.append(
                {
                    "name": cfg.name,
                    "path": str(yaml_file),
                    "hash": cfg.hash[:8],
                }
            )
        except Exception as e:
            # Skip invalid configs but log the error
            print(f"Error loading config {yaml_file}: {e}")
            continue

    return JSONResponse({"configs": sorted(configs, key=lambda x: x["name"])})


async def get_config(request: Request) -> JSONResponse:
    """Get a specific configuration by name."""
    name = request.path_params["name"]
    config_path = CONFIG_DIR / f"{name}.yml"

    if not config_path.exists():
        return JSONResponse(
            {"error": "Configuration not found"}, status_code=404
        )

    try:
        cfg = config_module.read_config(config_path)

        # Calculate wavelength using dispersion relation
        wavelength = compute_wavelength(
            cfg.water.wave_period, cfg.water.water_level
        )

        return JSONResponse(
            {
                "name": cfg.name,
                "hash": cfg.hash,
                "grid": cfg.grid.model_dump(),
                "water": {**cfg.water.model_dump(), "wavelength": wavelength},
                "breakwater": cfg.breakwater.model_dump(),
                "vegetation": cfg.vegetation.model_dump(),
                "numeric": cfg.numeric.model_dump(),
            }
        )
    except Exception as e:
        print(f"Error getting config {name}: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


async def create_config(request: Request) -> JSONResponse:
    """Create a new configuration."""
    data = await request.json()

    try:
        # Create config object from data
        cfg = config_module.Config(**data)

        # Write to file
        config_path = CONFIG_DIR / f"{cfg.name}.yml"
        config_module.write_config(cfg, config_path)

        return JSONResponse(
            {
                "name": cfg.name,
                "hash": cfg.hash,
                "path": str(config_path),
            },
            status_code=201,
        )
    except Exception as e:
        print(f"Error creating config: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=400)


async def update_config(request: Request) -> JSONResponse:
    """Update an existing configuration."""
    name = request.path_params["name"]
    data = await request.json()

    config_path = CONFIG_DIR / f"{name}.yml"
    if not config_path.exists():
        return JSONResponse(
            {"error": "Configuration not found"}, status_code=404
        )

    try:
        # Create updated config
        cfg = config_module.Config(**data)

        # Save with potentially new name
        new_path = CONFIG_DIR / f"{cfg.name}.yml"
        config_module.write_config(cfg, new_path)

        # Delete old file if name changed
        if name != cfg.name and config_path.exists():
            config_path.unlink()

        return JSONResponse(
            {
                "name": cfg.name,
                "hash": cfg.hash,
                "path": str(new_path),
            }
        )
    except Exception as e:
        print(f"Error updating config {name}: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=400)


async def delete_config(request: Request) -> JSONResponse:
    """Delete a configuration."""
    name = request.path_params["name"]
    config_path = CONFIG_DIR / f"{name}.yml"

    if not config_path.exists():
        return JSONResponse(
            {"error": "Configuration not found"}, status_code=404
        )

    try:
        config_path.unlink()
        return JSONResponse({"message": "Configuration deleted"})
    except Exception as e:
        print(f"Error deleting config {name}: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


async def simulate_config(request: Request) -> JSONResponse:
    """Run simulation for a configuration."""
    name = request.path_params["name"]
    config_path = CONFIG_DIR / f"{name}.yml"

    if not config_path.exists():
        return JSONResponse(
            {"error": "Configuration not found"}, status_code=404
        )

    try:
        # Load config and run simulation
        cfg = config_module.read_config(config_path)
        run_simulation(cfg)

        return JSONResponse(
            {
                "success": True,
                "message": "Simulation completed successfully",
            }
        )
    except Exception as e:
        print(f"Error running simulation for {name}: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


async def calculate_wavelength(request: Request) -> JSONResponse:
    """Calculate wavelength from wave period and water depth."""
    try:
        data = await request.json()
        wave_period = data.get("wave_period")
        water_level = data.get("water_level")

        if wave_period is None or water_level is None:
            return JSONResponse(
                {"error": "wave_period and water_level are required"},
                status_code=400,
            )

        wavelength = compute_wavelength(wave_period, water_level)

        return JSONResponse({"wavelength": wavelength})
    except Exception as e:
        print(f"Error calculating wavelength: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=400)


async def get_analysis_results(request: Request) -> JSONResponse:
    """Get analysis results for a configuration."""
    name = request.path_params["name"]
    config_path = CONFIG_DIR / f"{name}.yml"

    if not config_path.exists():
        return JSONResponse(
            {"error": "Configuration not found"}, status_code=404
        )

    try:
        # Load config to get hash
        cfg = config_module.read_config(config_path)
        simulation_dir = root_dir / "simulations" / f"{cfg.name}_{cfg.hash}"
        analysis_dir = simulation_dir / "analysis"

        # Check for the Plotly JSON file
        plot_file = analysis_dir / "water_levels_and_x_velocity.json"

        if not plot_file.exists():
            return JSONResponse(
                {"error": "Analysis results not found"}, status_code=404
            )

        # Load plot data
        import json

        with open(plot_file, "r") as f:
            plot_data = json.load(f)

        # Load wave statistics if available
        wave_stats_file = analysis_dir / "wave_statistics.csv"
        wave_stats = None
        if wave_stats_file.exists():
            import polars as pl

            wave_stats_df = pl.read_csv(wave_stats_file)
            wave_stats = wave_stats_df.to_dicts()

        return JSONResponse({"plot_data": plot_data, "wave_stats": wave_stats})
    except Exception as e:
        print(f"Error getting analysis results for {name}: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


def get_api_routes() -> List[Route]:
    """Get all API routes."""
    return [
        Route("/configs", list_configs, methods=["GET"]),
        Route("/configs", create_config, methods=["POST"]),
        Route("/configs/{name}", get_config, methods=["GET"]),
        Route("/configs/{name}", update_config, methods=["PUT"]),
        Route("/configs/{name}", delete_config, methods=["DELETE"]),
        Route("/simulate/{name}", simulate_config, methods=["POST"]),
        Route("/analysis/{name}", get_analysis_results, methods=["GET"]),
        Route("/wavelength", calculate_wavelength, methods=["POST"]),
    ]
