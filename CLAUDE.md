# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a SWASH (Simulating WAves till SHore) simulation framework for modeling breakwaters in wave channels and Baie-des-Bacon. The project provides a Python-based CLI and dashboard for configuring, running, and visualizing coastal engineering simulations.

## Key Commands

### Development Setup
```bash
# Install dependencies (requires Python 3.13+)
uv sync

# Format code
isort src/
black src/

# Lint code
ruff check src/
ty check src/

# Run type checking
ty check src/
```

### CLI Usage
```bash
# Create/update experiment configuration
cli create config/experiment.yml
# or shorthand
c create config/experiment.yml

# Run simulations (supports glob patterns)
cli run config/*.yml
# or shorthand
c run config/*.yml

# Launch interactive dashboard
cli dashboard
# or shorthand
c dashboard
```

## Architecture

### Configuration System
The project uses a hierarchical Pydantic-based configuration system:
- `Config` (root) contains `BreakwaterConfig`, `WaterConfig`, `VegetationConfig`, `NumericConfig`
- Configurations are validated and hashed for reproducibility
- YAML files with comments are generated using ruamel.yaml

### Template System
SWASH input files are generated using Jinja2 templates:
- Template location: `templates/INPUT`
- Variables are injected from the configuration models
- Generated files are placed in `simulations/<name>_<hash>/`

### Key Modules
- `src/cli.py`: Typer-based CLI with create/run/dashboard commands
- `src/config.py`: Pydantic models for configuration validation
- `src/simulation.py`: Simulation execution logic (in development)
- `src/dashboard/`: Dash-based web interface (in development)

## Development Notes

### Code Style
- Line length: 79 characters (enforced by Black)
- Import sorting: Black-compatible profile
- Type hints are used throughout

### Output Structure
Simulations create directories with format: `simulations/<name>_<hash>/`
- Each simulation is uniquely identified by configuration hash
- Results are cached based on configuration content

### SWASH Integration
- User manual: `docs/swash_manual.md`
- Input templates use Jinja2 syntax for variable substitution
- The framework handles SWASH execution and output parsing
- IMPORTANT: First refer to `@docs/swash_manual/swash_1d_config_summary.md` when working with swash

### Project Documentation
- `docs/swash_manual.md`: SWASH user manual for reference
- `docs/overflowing_report.md`: Experimental protocol for hydrodynamic behavior of vegetated breakwaters (in French)
- `docs/stability_report.md`: Armourstone design analysis for low-crested breakwaters in Baie des Bacon

### Commit Guidelines
- NEVER mention Claude, Claude Code, or Anthropic in commit messages

### File Format Notes
- Files ending with .dat are text files and not binary ones

### Running the Program
To run the program, use the following steps:

1. Ensure all dependencies are installed:
```bash
uv sync
```

2. Create a configuration file for your experiment:
```bash
cli create config/my_experiment.yml
```

3. Run the simulation using the created configuration:
```bash
cli run config/my_experiment.yml
```

4. Optional: Launch the interactive dashboard to visualize results:
```bash
cli dashboard
```

Note: Use the shorthand `c` instead of `cli` for quicker command entry (e.g., `c run config/my_experiment.yml`).