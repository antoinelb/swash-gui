# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Code Documentation Guidelines
- Code explanations should be in function docstrings
- Write comments only if they are absolutely necessary to understand a code chunk
- Never write module docstrings

## Commands

### Development Environment
```bash
# Install dependencies
uv sync

# Run with development dependencies
uv sync --group dev
```

### Testing and Code Quality
```bash
# Run tests
pytest

# Code formatting and linting
black src/
isort src/
ruff check src/

# Type checking
ty check src
```

### CLI Usage
```bash
# Main CLI entry points
swg --help

# Common operations
swg create config/experiment.yml    # Create config
swg run config/experiment.yml       # Run simulation
swg dashboard                       # Launch web UI
swg analyze config/experiment.yml   # Analyze results
swg clean                           # Clean orphaned sims
```

### Dashboard Development
```bash
# Start dashboard server
python -m src.cli dashboard
# Runs on http://localhost:8000 with hot reload
```

## Architecture

### Core Components

**Configuration System (`src/config.py`)**
- Pydantic models for type-safe configuration management
- YAML-based config files with automatic validation
- Hash-based simulation directory naming for reproducibility
- Modular configs: Grid, Breakwater, Water, Vegetation, Numeric

**Simulation Engine (`src/simulation.py`)**
- Jinja2 template rendering for SWASH INPUT files
- Automatic generation of bathymetry, porosity, and vegetation files
- SWASH process execution with real-time progress monitoring
- Post-simulation analysis integration

**Web Dashboard (`src/dashboard/`)**
- Starlette backend with vanilla JS frontend
- SPA architecture with client-side routing
- Real-time breakwater visualization with cross-section diagrams
- RESTful API for config management and simulation control

**CLI Interface (`src/cli.py`)**
- Typer-based CLI with short aliases (c, r, d, cc, a)
- Glob pattern support for batch operations
- Orphaned simulation cleanup functionality

### Data Flow

1. **Configuration**: YAML files in `config/` define simulation parameters
2. **Template Processing**: Jinja2 renders SWASH INPUT from `templates/INPUT`
3. **File Generation**: Creates bathymetry, porosity, vegetation data files
4. **Simulation**: Executes SWASH in `simulations/<name>_<hash>/swash/`
5. **Analysis**: Generates plots and results in simulation directory

### Key Patterns

**Hash-based Versioning**: Each config generates a unique hash used for simulation directory naming, ensuring reproducibility and preventing config drift.

**Template-driven INPUT Generation**: SWASH input files are generated from Jinja2 templates with access to full configuration objects, enabling complex conditional logic.

**Modular Configuration**: Separate Pydantic models for different simulation aspects allow independent validation and selective updates.

**Progressive File Creation**: Simulation files are only created when their corresponding features are enabled (e.g., vegetation files only when `vegetation.enable=True`).

## External Dependencies

- **SWASH**: Must be installed and available in PATH for simulation execution
- **Templates**: `templates/INPUT` contains the base SWASH input template
- **Static Assets**: Dashboard frontend assets in `src/dashboard/static/`

## Configuration Management

Configurations use hierarchical validation with automatic hash generation. When modifying configs:
- Use the dashboard for guided editing with real-time validation
- CLI `create` command initializes configs with sensible defaults
- All changes update the configuration hash, triggering new simulation directories

## Web Scraping and Automation Guidelines
- Always close browser tabs/puppeteer browser instances after task completion to free up system resources