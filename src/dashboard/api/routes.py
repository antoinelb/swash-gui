from pathlib import Path
from typing import List

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from src import config as config_module
from src.simulation import run_simulation

CONFIG_DIR = Path("config")


async def list_configs(request: Request) -> JSONResponse:
    """List all available configurations."""
    if not CONFIG_DIR.exists():
        return JSONResponse({"configs": []})
    
    configs = []
    for yaml_file in CONFIG_DIR.glob("*.yml"):
        try:
            cfg = config_module.read_config(yaml_file)
            configs.append({
                "name": cfg.name,
                "path": str(yaml_file),
                "hash": cfg.hash[:8],
            })
        except Exception as e:
            # Skip invalid configs
            continue
    
    return JSONResponse({"configs": sorted(configs, key=lambda x: x["name"])})


async def get_config(request: Request) -> JSONResponse:
    """Get a specific configuration by name."""
    name = request.path_params["name"]
    config_path = CONFIG_DIR / f"{name}.yml"
    
    if not config_path.exists():
        return JSONResponse({"error": "Configuration not found"}, status_code=404)
    
    try:
        cfg = config_module.read_config(config_path)
        return JSONResponse({
            "name": cfg.name,
            "hash": cfg.hash,
            "grid": cfg.grid.model_dump(),
            "breakwater": cfg.breakwater.model_dump(),
            "water": cfg.water.model_dump(),
            "vegetation": cfg.vegetation.model_dump(),
            "numeric": cfg.numeric.model_dump(),
        })
    except Exception as e:
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
        
        return JSONResponse({
            "name": cfg.name,
            "hash": cfg.hash,
            "path": str(config_path),
        }, status_code=201)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def update_config(request: Request) -> JSONResponse:
    """Update an existing configuration."""
    name = request.path_params["name"]
    data = await request.json()
    
    config_path = CONFIG_DIR / f"{name}.yml"
    if not config_path.exists():
        return JSONResponse({"error": "Configuration not found"}, status_code=404)
    
    try:
        # Create updated config
        cfg = config_module.Config(**data)
        
        # Save with potentially new name
        new_path = CONFIG_DIR / f"{cfg.name}.yml"
        config_module.write_config(cfg, new_path)
        
        # Delete old file if name changed
        if name != cfg.name and config_path.exists():
            config_path.unlink()
        
        return JSONResponse({
            "name": cfg.name,
            "hash": cfg.hash,
            "path": str(new_path),
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def delete_config(request: Request) -> JSONResponse:
    """Delete a configuration."""
    name = request.path_params["name"]
    config_path = CONFIG_DIR / f"{name}.yml"
    
    if not config_path.exists():
        return JSONResponse({"error": "Configuration not found"}, status_code=404)
    
    try:
        config_path.unlink()
        return JSONResponse({"message": "Configuration deleted"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def simulate_config(request: Request) -> JSONResponse:
    """Run simulation for a configuration."""
    name = request.path_params["name"]
    config_path = CONFIG_DIR / f"{name}.yml"
    
    if not config_path.exists():
        return JSONResponse({"error": "Configuration not found"}, status_code=404)
    
    try:
        # Run simulation (this should be async in production)
        result = run_simulation(config_path)
        
        return JSONResponse({
            "success": result,
            "message": "Simulation started" if result else "Simulation failed",
        })
    except Exception as e:
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
    ]