# SWASH GUI Overview

This framework provides a Python-based interface for configuring, running, and analyzing [SWASH](https://swash.sourceforge.io/) (Simulating WAves till SHore) simulations, specifically designed for modeling coastal structures like breakwaters and vegetation.

## What is SWASH?

SWASH is a non-hydrostatic wave-flow model capable of simulating:
- Wave propagation from deep water to the shoreline
- Wave breaking and runup
- Flow through porous structures (breakwaters)
- Wave-vegetation interaction
- Overtopping and flooding

## Framework Architecture

### High-Level Workflow

```
YAML Config → Validation → Template Rendering → SWASH Execution → Analysis
     ↓            ↓              ↓                    ↓              ↓
config.yml    Pydantic      Jinja2 INPUT         swash.exe     Python plots
              models        + data files          process      
```

### Key Components

1. **Configuration System** (`src/config.py`)
   - Type-safe YAML configuration using Pydantic models
   - Automatic validation of parameters
   - Hash-based versioning for reproducibility

2. **Template Engine** (`templates/INPUT`)
   - Jinja2 templates convert configs to SWASH input format
   - Conditional sections based on enabled features
   - Dynamic file generation (bathymetry, porosity, vegetation)

3. **Simulation Manager** (`src/simulation.py`)
   - Handles SWASH process execution
   - Real-time progress monitoring
   - Output file organization

4. **Analysis Tools** (`src/analysis.py`)
   - Automated post-processing
   - Wave statistics calculation
   - Visualization generation

5. **User Interfaces**
   - CLI (`swg`) for batch processing
   - Web dashboard for interactive configuration and visualization

## Core Concepts

### Hash-Based Versioning

Each configuration generates a unique hash that:
- Ensures reproducibility
- Prevents accidental overwrites
- Tracks configuration changes
- Creates unique simulation directories

Example: `model001_c610e7bc/` where `c610e7bc` is the config hash

### Modular Configuration

The configuration is split into logical sections:
- **Grid**: Computational domain setup
- **Water**: Wave and water properties
- **Breakwater**: Structure geometry and properties (optional)
- **Vegetation**: Plant characteristics (optional)
- **Numeric**: Simulation control parameters

### File Generation

The framework automatically generates required SWASH input files:
- `bathymetry.txt`: Seafloor elevation profile
- `porosity.txt`: Spatial porosity distribution
- `structure_height.txt`: Breakwater geometry
- `vegetation_density.txt`: Plant density distribution

### Output Organization

Each simulation creates a structured directory:
```
simulations/
└── experiment_name_hash/
    ├── config.yml          # Copy of configuration
    ├── swash/              # SWASH working directory
    │   ├── INPUT           # Generated input file
    │   ├── PRINT           # SWASH output log
    │   ├── *.txt           # Data files
    │   ├── wg*.txt         # Wave gauge outputs
    │   └── data.csv        # Combined data for all gauges
    └── analysis/           # Post-processing results
        ├── *.png           # Plots
        └── *.json          # Extracted data
```

## Integration with SWASH

### Input File Generation

The framework translates high-level configuration parameters into SWASH commands:

1. **Physical Setup**: Grid dimensions, water depth, wave conditions
2. **Structure Definition**: Breakwater geometry via bottom elevation and porosity
3. **Boundary Conditions**: Wave generation and absorption
4. **Physics Options**: Non-hydrostatic pressure, breaking, friction
5. **Output Requests**: Wave gauges, spatial fields, statistics

### Process Management

- Executes SWASH as a subprocess
- Captures and logs all output
- Monitors for errors and warnings
- Provides real-time progress updates

### Post-Processing

Automatically extracts and visualizes:
- Time series at wave gauge locations
- Wave height evolution along the channel

## Advantages of This Approach

1. **Reproducibility**: Hash-based versioning ensures experiments can be recreated
2. **Validation**: Pydantic models catch configuration errors before simulation
3. **Automation**: Batch processing of multiple configurations
4. **Visualization**: Immediate feedback through plots and web interface
5. **Organization**: Structured output directories for easy data management
6. **Flexibility**: Template system allows customization without code changes

## Next Steps

- [Configuration Reference](configuration-reference.md) - Detailed parameter documentation
- [Template Mapping](template-mapping.md) - How configs map to SWASH input
- [SWASH Physics](swash-physics.md) - Understanding the numerical model
- [Output Interpretation](output-interpretation.md) - Analyzing simulation results
