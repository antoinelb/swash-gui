# SWASH Breakwater Simulation Framework

A Python-based framework for modeling breakwaters in wave channels and Baie-des-Bacon using [SWASH](https://swash.sourceforge.io/) (Simulating WAves till SHore). This project provides a CLI and web dashboard for configuring, running, and visualizing coastal engineering simulations.

## Features

- **Interactive Web Dashboard**: Visual configuration management with real-time breakwater cross-section diagrams
- **CLI Interface**: Command-line tools for batch processing and automation
- **Configuration Management**: YAML-based configuration with validation and reproducibility tracking
- **Template System**: Jinja2-powered SWASH input file generation
- **Modular Design**: Separate components for breakwater geometry, waves, vegetation, and numerical parameters

## Project Structure

```
├── config/           # Configuration files (.yml)
├── docs/             # Documentation and manuals
├── src/              # Source code
│   ├── cli.py        # Command-line interface
│   ├── config.py     # Configuration models and validation
│   ├── simulation.py # Simulation execution logic
│   └── dashboard/    # Web dashboard (Starlette + vanilla JS)
├── templates/        # SWASH input file templates
├── simulations/      # Generated simulation directories
└── experiments/      # Reference experiments
```

## Installation

### Prerequisites

- **Python 3.13+**: Required for the simulation framework
- **SWASH**: Numerical wave simulation software
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
4. Ensure `swash` is available in your system PATH (it may be called swash.exe)

### 3. Verify Installation

```bash
# Test Python framework
python -m src.cli --help

# Test SWASH installation
swash --version
```

## Quick Start

### 1. Create Your First Configuration

```bash
# Create a new configuration file
python -m src.cli create config/my-experiment.yml
```

This creates a YAML file with default parameters that you can edit:

```yaml
grid:
  length: 112.0        # Domain length (m)
  nx_cells: 500        # Number of grid cells
  n_layers: 2          # Vertical layers

breakwater:
  crest_height: 2.0    # Height above seafloor (m)
  crest_width: 2.0     # Crest width (m)
  slope: 2.0           # Side slope (H:V ratio)
  porosity: 0.4        # Porosity coefficient

water:
  water_level: 1.0     # Still water level (m)
  wave_height: 0.5     # Wave height (m)
  wave_period: 6.0     # Wave period (s)

numeric:
  breakwater_start_position: 100.0  # Breakwater location (m)
  wave_gauge_positions: [20.0, 60.0, 65.0, 80.0, 100.0]
```

### 2. Launch the Web Dashboard

```bash
# Start the interactive dashboard
python -m src.cli dashboard
```

Open your browser to [http://localhost:8000](http://localhost:8000) to:
- Visualize breakwater cross-sections
- Edit configuration parameters
- Run simulations
- View results

### 3. Run Simulations via CLI

```bash
# Run a single simulation
python -m src.cli run config/my-experiment.yml

# Run multiple configurations
python -m src.cli run config/*.yml
```

## Configuration Reference

### Breakwater Parameters

- **crest_height**: Height of breakwater crest above seafloor (m)
- **crest_width**: Width of the breakwater crest (m)  
- **slope**: Side slope ratio (horizontal:vertical, e.g., 2:1)
- **porosity**: Porosity coefficient (0-1)
- **armour_dn50**: Median diameter of armor stones (m)

### Wave Conditions

- **water_level**: Still water level above seafloor (m)
- **wave_height**: Regular wave height (m)
- **wave_period**: Wave period (s)
- **water_density**: Water density (kg/m³)

### Vegetation (Optional)

- **enable**: Enable vegetation on breakwater crest
- **plant_height**: Height of vegetation (m)
- **plant_density**: Number of stems per m²
- **drag_coefficient**: Vegetation drag coefficient

### Numerical Settings

- **n_waves**: Number of wave cycles to simulate
- **time_step**: Initial time step (s, auto-adjusted)
- **breakwater_start_position**: X-coordinate of breakwater start (m)
- **wave_gauge_positions**: List of wave gauge X-coordinates (m)

## Output Files

Each simulation creates a directory `simulations/<name>_<hash>/` containing:

- **INPUT**: SWASH input file generated from template
- **bathymetry.dat**: Seafloor elevation data
- **porosity.dat**: Breakwater porosity field
- **structure_height.dat**: Breakwater geometry
- **wg*.dat**: Wave gauge time series data
- **final_state.mat**: Final simulation state

## Documentation

📚 **[Complete Documentation](docs/README.md)** - Comprehensive guides covering all aspects of the framework

### Quick Links
- **[Getting Started](docs/swash-overview.md)** - Project overview and introduction
- **[Simulation Workflow](docs/simulation-workflow.md)** - How to run simulations
- **[Configuration Guide](docs/configuration-guide.md)** - Parameter setup and management
- **[Physics & Parameters](docs/physics-and-parameters.md)** - Scientific foundation
- **[Output Analysis](docs/output-reference.md)** - Understanding results
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

### Reference Material
- **[INPUT File Reference](docs/input-file-reference.md)** - SWASH input file details
- **[Breakwater Design](docs/breakwater-design.md)** - Physical structure details
- **SWASH Manual**: `docs/swash_manual.md` - Complete SWASH user reference

## Troubleshooting

### Common Issues

1. **SWASH not found**: Ensure SWASH is installed and in your PATH
2. **Permission errors**: Check file permissions in simulation directories  
3. **Configuration errors**: Use the dashboard for guided parameter editing
4. **Memory issues**: Reduce grid resolution (`nx_cells`) for large domains

### Getting Help

- Check existing configurations in `config/` for examples
- Review the SWASH manual for parameter guidance
- Use the web dashboard for visual parameter validation
