# SWASH Wave-Structure Interaction Framework

A Python-based framework for configuring, running, and analyzing [SWASH](https://swash.sourceforge.io/) (Simulating WAves till SHore) simulations. Designed for modeling coastal structures like breakwaters with optional vegetation, providing a streamlined interface for coastal engineering research.

## Features

- **Interactive Web Dashboard**: Visual configuration management with real-time breakwater cross-section diagrams
- **CLI Interface**: Command-line tools for batch processing and automation (`swg` command)
- **Configuration Management**: YAML-based configuration with validation and hash-based versioning
- **Template System**: Jinja2-powered SWASH input file generation
- **Automated Analysis**: Post-processing with statistical analysis and visualization
- **Modular Design**: Separate components for breakwater geometry, waves, vegetation, and numerical parameters

## Documentation

📚 **Local Documentation** - Comprehensive guides in the `docs/` directory:

- [Framework Overview](docs/README.md) - Introduction and architecture
- [Configuration Reference](docs/configuration-reference.md) - Detailed parameter documentation
- [SWASH Physics](docs/swash-physics.md) - Physical processes and numerical methods
- [Output Interpretation](docs/output-interpretation.md) - Understanding simulation results
- [Template Mapping](docs/template-mapping.md) - How configurations map to SWASH input
- [Troubleshooting Guide](docs/troubleshooting-guide.md) - Common issues and solutions

### Quick Reference Guides

- [Config Quick Reference](docs/quick-ref/config-quick-ref.md) - Common configurations
- [SWASH Commands](docs/quick-ref/swash-commands.md) - Essential SWASH input commands

### SWASH Manual

- [SWASH Manual Summary](docs/swash_manual/swash_1d_config_summary.md) - 1D configuration guide
- [Complete SWASH Manual](docs/swash_manual/swash_manual.md) - Full reference

## Installation

### Prerequisites

- **Python 3.13+**: Required for the simulation framework
- **SWASH**: Numerical wave simulation software (must be in PATH)
- **uv**: Fast Python package manager (recommended)

### 1. Install Python Dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

### 2. Install SWASH

1. Visit [SWASH Downloads](https://swash.sourceforge.io/download/download.htm)
2. Download the appropriate version for your operating system
3. Follow the installation instructions for your platform
4. Ensure `swash` is available in your system PATH

### 3. Verify Installation

```bash
# Test Python framework
swg --help

# Test SWASH installation
swash -v
```

## Quick Start

### 1. Create Your First Configuration

```bash
# Create a new configuration file with default parameters
swg create config/my-experiment.yml
```

This creates a YAML file with validated parameters:

```yaml
grid:
  # Grid configuration is managed internally
  
water:
  water_level: 1.0         # Still water level (m)
  water_density: 1000.0    # Water density (kg/m³)
  wave_height: 0.5         # Regular wave height (m)
  wave_period: 6.0         # Wave period (s)

breakwater:
  enable: true             # Enable breakwater
  crest_height: 2.0        # Height above seafloor (m)
  crest_length: 2.0        # Crest length (m)
  slope: 2.0               # Side slope (H:V ratio)
  porosity: 0.4            # Porosity coefficient
  stone_density: 2700.0    # Stone density (kg/m³)
  armour_dn50: 0.3         # Median stone diameter (m)
  breakwater_start_position: 70.0  # X-coordinate (m)

vegetation:
  enable: false            # Enable vegetation on crest
  type:
    plant_height: 0.3      # Plant height (m)
    plant_diameter: 0.01   # Stem diameter (m)
    plant_density: 100.0   # Stems per m²
    drag_coefficient: 1.0  # Drag coefficient
  distribution: half       # 'half', 'alternating', or 'custom'

numeric:
  n_waves: 50              # Number of wave cycles
  wave_gauge_positions:    # Measurement locations (m)
    - 20.0
    - 60.0
    - 65.0
    - 80.0
    - 100.0
```

### 2. Launch the Web Dashboard

```bash
# Start the interactive dashboard
swg dashboard
# or
swg d
```

Open your browser to [http://localhost:8000](http://localhost:8000) to:
- Create and edit configurations visually
- See real-time breakwater cross-section diagrams
- Run simulations with progress monitoring
- View analysis results and plots

### 3. Run Simulations via CLI

```bash
# Run a single simulation
swg run config/my-experiment.yml
# or
swg r config/my-experiment.yml

# Run multiple configurations
swg run config/*.yml

# Analyze existing results
swg analyze config/my-experiment.yml
# or
swg a config/my-experiment.yml
```

### 4. Clean Up

```bash
# Remove orphaned simulation directories
swg clean
# or
swg cc
```

## Project Structure

```
├── config/              # Configuration files (.yml)
├── docs/                # Documentation
│   ├── README.md        # Framework overview
│   ├── configuration-reference.md
│   ├── swash-physics.md
│   └── ...
├── src/                 # Source code
│   ├── cli.py           # Command-line interface
│   ├── config.py        # Configuration models (Pydantic)
│   ├── simulation.py    # SWASH execution engine
│   ├── analysis.py      # Post-processing tools
│   └── dashboard/       # Web interface
│       ├── app.py       # Starlette backend
│       └── static/      # Frontend (vanilla JS)
├── templates/           # SWASH input templates
│   └── INPUT            # Jinja2 template
├── simulations/         # Generated simulation directories
│   └── name_hash/       # Hash-versioned outputs
└── pyproject.toml       # Project configuration
```

## Configuration System

### Hash-Based Versioning

Each configuration generates a unique hash that:
- Ensures reproducibility of experiments
- Prevents accidental overwrites
- Creates unique simulation directories
- Tracks configuration evolution

Example: `model001_c610e7bc/` where `c610e7bc` is the configuration hash

### Validation

All parameters are validated using Pydantic models:
- Type checking (numeric ranges, string formats)
- Physical constraints (wave steepness, grid resolution)
- Dependency validation (vegetation requires breakwater)
- Automatic hash generation

## Output Files

Each simulation creates a directory `simulations/<name>_<hash>/` containing:

### SWASH Files
- `INPUT` - Generated SWASH input file
- `PRINT` - SWASH execution log
- `bathymetry.txt` - Seafloor elevation profile
- `porosity.txt` - Breakwater porosity field (if enabled)
- `structure_height.txt` - Breakwater geometry (if enabled)
- `vegetation_density.txt` - Plant density (if enabled)
- `wg01.txt`, `wg02.txt`, ... - Wave gauge time series
- `data.csv` - Consolidated wave gauge data
- `final_state.mat` - Final spatial state (MATLAB format)

### Analysis Outputs
- `water_levels_and_x_velocity.png` - Statistical box plots
- `water_levels_and_x_velocity.json` - Plot data for dashboard

## CLI Commands

All commands have short aliases for convenience:

| Command | Alias | Description |
|---------|-------|-------------|
| `swg create` | `swg c` | Create/update configuration files |
| `swg run` | `swg r` | Run SWASH simulations |
| `swg dashboard` | `swg d` | Launch web interface |
| `swg analyze` | `swg a` | Analyze simulation results |
| `swg clean` | `swg cc` | Clean orphaned directories |

## Physical Modeling

The framework models:
- **Wave propagation** and transformation
- **Wave breaking** using energy dissipation
- **Porous flow** through breakwater structures
- **Vegetation drag** forces on flow
- **Overtopping** and transmission
- **Bottom friction** using Manning's formula

See [SWASH Physics](docs/swash-physics.md) for detailed equations and theory.

## Troubleshooting

### Common Issues

1. **SWASH not found**: Ensure SWASH executable is in your PATH
2. **Permission errors**: Check write permissions in simulation directories
3. **Memory issues**: Reduce grid resolution or domain size
4. **Numerical instability**: Check CFL condition and time step

### Getting Help

- Use `swg --help` for command documentation
- Check the [Troubleshooting Guide](docs/troubleshooting-guide.md)
- Review example configurations in `config/`
- Examine SWASH output in `PRINT` files

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Format code
black src/
isort src/

# Lint
ruff check src/

# Type checking
ty check src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this framework in your research, please cite:
- The SWASH model: [Zijlema et al. (2011)](https://doi.org/10.1016/j.coastaleng.2011.05.015)
- This framework: [GitHub repository](https://github.com/antoinelb/swash-gui)
