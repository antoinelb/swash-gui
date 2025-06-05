# Configuration Guide

## Overview

The SWASH breakwater modeling framework uses a hierarchical configuration system built on **Pydantic** and **YAML** to manage simulation parameters. This system provides automatic validation, type checking, and reproducible experiment tracking through configuration hashing.

## Configuration Architecture

### Hierarchical Structure

The configuration is organized into logical groups:

```yaml
# Main configuration file (e.g., config/dev.yml)
name: experiment_name          # Derived from filename
hash: auto_generated          # Overall configuration hash

grid:                         # Computational domain
  hash: auto_generated       
  length: 112.0              # Domain length (m)
  nx_cells: 500              # Grid resolution
  n_layers: 2                # Vertical layers

breakwater:                   # Structure geometry and materials
  hash: auto_generated
  crest_height: 2.0          # Structure dimensions
  crest_width: 3.0
  slope: 1.75                # Side slopes
  porosity: 0.4              # Material properties
  # ... additional parameters

water:                        # Hydraulic conditions
  hash: auto_generated
  water_level: 1.0           # Still water level
  wave_height: 0.6           # Wave conditions
  wave_period: 6.0
  water_density: 1000.0      # Fluid properties

vegetation:                   # Vegetation characteristics
  hash: auto_generated
  enable: true               # Toggle vegetation
  plant_height: 0.5          # Plant geometry
  plant_density: 10.0        # Density and drag
  # ... additional parameters

numeric:                      # Simulation control
  hash: auto_generated
  n_waves: 50                # Duration
  breakwater_start_position: 100.0  # Positioning
  wave_gauge_positions: [...]       # Instrumentation
  # ... additional parameters
```

### Validation and Type Safety

Each parameter is validated using **Pydantic** with:
- **Type checking**: Ensures correct data types (float, int, bool, list)
- **Range validation**: Can be extended for physical constraints
- **Default values**: Sensible defaults for all parameters
- **Automatic documentation**: Descriptions embedded in the schema

## Configuration Groups

### 1. Grid Configuration (`grid`)

Controls the computational domain discretization:

```yaml
grid:
  length: 112.0              # Domain length in meters
  nx_cells: 500              # Number of computational cells
  n_layers: 2                # Vertical layers (2-3 recommended)
```

**Key considerations:**
- **Grid resolution**: `dx = length / nx_cells` determines spatial accuracy
- **Vertical layers**: More layers = better vertical resolution but higher computational cost
- **Domain length**: Should be sufficient for wave development and absorption

### 2. Breakwater Configuration (`breakwater`)

Defines the physical structure:

```yaml
breakwater:
  # Geometry
  crest_height: 2.0          # Height above bottom (m)
  crest_width: 3.0           # Crest width (m)  
  slope: 1.75                # Side slope (H:V ratio)
  
  # Material properties
  porosity: 0.4              # Void fraction (0-1)
  stone_density: 2600.0      # Rock density (kg/m³)
  
  # Stone size distribution
  armour_dn50: 1.15          # Armour stone median diameter (m)
  filter_dn50: 0.5           # Filter layer median diameter (m)
  core_dn50: 0.2             # Core material median diameter (m)
```

**Physical relationships:**
- **Freeboard**: `crest_height - water_level` determines overtopping
- **Relative density**: `Δ = (stone_density - water_density) / water_density`
- **Structure width**: Automatically calculated from geometry

### 3. Water Configuration (`water`)

Sets hydraulic and wave conditions:

```yaml
water:
  # Basic conditions
  water_level: 1.0           # Still water level (m)
  water_density: 1000.0      # Water density (kg/m³)
  
  # Wave parameters
  wave_height: 0.6           # Regular wave height (m)
  wave_period: 6.0           # Wave period (s)
```

**Design considerations:**
- **Wave steepness**: `H/L` should be realistic (typically < 0.1)
- **Relative depth**: `h/L` determines intermediate vs. shallow water
- **Freeboard**: `water_level - crest_height` affects overtopping behavior

### 4. Vegetation Configuration (`vegetation`)

Controls vegetation modeling:

```yaml
vegetation:
  enable: true               # Enable/disable vegetation
  
  # Plant characteristics
  plant_height: 0.5          # Height above crest (m)
  plant_diameter: 0.01       # Effective stem diameter (m)
  plant_density: 10.0        # Stems per square meter
  drag_coefficient: 1.0      # Drag coefficient
```

**Modeling notes:**
- **Enable/disable**: Allows comparison of vegetated vs. non-vegetated scenarios
- **Realistic parameters**: Based on coastal vegetation species (Rosa rugosa, Alnus viridis)
- **Seasonal variation**: Adjust `plant_density` and `drag_coefficient` for different seasons
- **Spatial application**: Vegetation automatically placed only on breakwater crest
- **Crest zone**: Calculated as structure extent minus side slopes

### 5. Numeric Configuration (`numeric`)

Controls simulation execution and output:

```yaml
numeric:
  # Simulation control
  n_waves: 50                # Number of waves to simulate
  time_step: 0.05            # Initial time step (s)
  
  # Positioning
  breakwater_start_position: 100.0  # Structure location (m)
  
  # Instrumentation
  wave_gauge_positions:      # Gauge locations (m)
    - 20.0                   # Incident conditions
    - 60.0                   # Pre-structure
    - 65.0                   # Near structure
    - 80.0                   # Close to structure
    - 100.0                  # At structure
  
  # Output control
  output_interval: 0.1       # Time interval for output (s)
```

**Simulation considerations:**
- **Duration**: `n_waves × wave_period` determines total simulation time
- **Time stepping**: SWASH uses adaptive time stepping starting from `time_step`
- **Gauge positioning**: Strategic placement for incident, transmitted, and reflected waves

## Configuration Management

### Creating Configurations

#### 1. Using the CLI
```bash
# Create a new configuration file
swg create config/new_experiment.yml

# This generates a YAML file with default values and comments
```

#### 2. Manual Creation
```yaml
# config/custom.yml
grid:
  length: 112.0
  nx_cells: 500
  n_layers: 2

breakwater:
  crest_height: 2.5          # Higher crest
  crest_width: 4.0           # Wider crest
  slope: 2.0                 # Gentler slopes
  porosity: 0.3              # Lower porosity

water:
  water_level: 1.5           # Higher water level
  wave_height: 0.8           # Larger waves
  wave_period: 8.0           # Longer period

vegetation:
  enable: true
  plant_density: 15.0        # Denser vegetation

numeric:
  n_waves: 100               # Longer simulation
  breakwater_start_position: 90.0  # Different position
```

### Configuration Hashing

Each configuration section and the overall configuration receive unique hashes:

```yaml
hash: 58ab2fe7              # Overall configuration hash
grid:
  hash: f144f5d3            # Grid-specific hash
breakwater:
  hash: d8acf8fb            # Breakwater-specific hash
# ... etc.
```

**Benefits:**
- **Reproducibility**: Same configuration = same hash = same results
- **Change tracking**: Different hashes indicate parameter changes
- **Result organization**: Simulation directories named with configuration hash

### Validation and Error Handling

The system automatically validates:

#### Type Checking
```yaml
# Valid
wave_height: 0.6            # float
n_waves: 50                 # int
enable: true                # bool

# Invalid - will raise validation error
wave_height: "medium"       # string instead of float
n_waves: 50.5               # float instead of int
```

#### Range Validation (Future Enhancement)
```python
# Example of additional validation that could be added
wave_height: float = pydantic.Field(
    default=0.5, 
    gt=0.0,                # Must be positive
    lt=10.0,               # Reasonable upper limit
    description="Wave height for regular waves (m)"
)
```

## Advanced Configuration

### Parametric Studies

Create multiple configurations for parameter studies:

```bash
# Base configuration
config/base.yml

# Variations
config/base_h05.yml         # wave_height: 0.5
config/base_h08.yml         # wave_height: 0.8
config/base_h12.yml         # wave_height: 1.2

# Run all variations
swg run config/base_*.yml
```

### Template Variables

The configuration supports calculated properties:

```python
# Automatically calculated in the Config class
@property
def simulation_duration(self) -> float:
    """Total simulation time in seconds"""
    return self.numeric.n_waves * self.water.wave_period

@property  
def breakwater_end_position(self) -> float:
    """End position of breakwater structure"""
    base_width = self.breakwater.crest_width + 2 * (
        self.breakwater.crest_height * self.breakwater.slope
    )
    return self.numeric.breakwater_start_position + base_width
```

### Configuration Inheritance

While not currently implemented, the system could support:

```yaml
# base.yml
extends: base_configuration.yml
overrides:
  water:
    wave_height: 0.8        # Override specific parameters
  vegetation:
    plant_density: 15.0
```

## Best Practices

### 1. Naming Conventions
- **Descriptive names**: Use clear, descriptive filenames
- **Systematic naming**: For parameter studies, use consistent naming patterns
- **Version control**: Include configuration files in version control

### 2. Parameter Selection
- **Physical realism**: Ensure parameters represent realistic conditions
- **Consistent units**: All parameters use SI units (meters, seconds, kg/m³)
- **Documentation**: Add comments to explain non-obvious parameter choices

### 3. Validation Workflow
```bash
# Test configuration before long simulations
swg run config/test.yml     # Quick validation run

# Check generated INPUT file
cat simulations/test_<hash>/INPUT  # Review SWASH input

# Run full simulation
swg run config/production.yml
```

### 4. Backup and Documentation
- **Configuration backup**: Keep copies of important configurations
- **Parameter documentation**: Document parameter choices in README files
- **Result linking**: Link simulation results to configuration hashes

## Troubleshooting

### Common Configuration Errors

#### 1. Invalid YAML Syntax
```yaml
# Incorrect indentation
water:
wave_height: 0.6            # Missing indentation

# Solution: Check YAML syntax
water:
  wave_height: 0.6
```

#### 2. Type Mismatches
```yaml
# Incorrect: string instead of number
n_waves: "50"

# Correct: proper numeric type
n_waves: 50
```

#### 3. Missing Required Parameters
```yaml
# Incorrect: missing name
grid:
  length: 112.0

# Correct: filename provides name automatically
# Or explicitly specify name field
```

#### 4. Unrealistic Parameter Combinations
```yaml
# Problematic: very steep waves
wave_height: 2.0
wave_period: 3.0            # H/L ≈ 0.2 (very steep)

# Better: more realistic steepness
wave_height: 0.6
wave_period: 6.0            # H/L ≈ 0.02 (realistic)
```

## Next Steps

- **[Input File Reference](input-file-reference.md)**: See how configurations become SWASH input
- **[Simulation Workflow](simulation-workflow.md)**: Learn to run simulations with configurations  
- **[Physics and Parameters](physics-and-parameters.md)**: Understand the physical meaning of parameters
- **[Troubleshooting](troubleshooting.md)**: Solutions for common configuration issues