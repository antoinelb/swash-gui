# Configuration Reference

This document provides a complete reference for all configuration parameters in the SWASH simulation framework. Parameters are organized by configuration section, with details on types, defaults, validation, and their corresponding SWASH commands.

## Overview

The configuration system uses Pydantic models with YAML serialization for type-safe parameter management. Each configuration section has an automatically generated hash for reproducibility tracking.

## Computational Grid Configuration

The computational grid defines the simulation domain. Most parameters are fixed for consistency.

### Fixed Parameters

| Parameter | Value | Unit | Description |
|-----------|--------|------|-------------|
| `grid.length` | 112.0 | m | Total domain length |
| `grid.nx_cells` | 500 | - | Number of grid cells |
| `grid.n_layers` | 2 | - | Vertical layers |

**SWASH Commands:**
```
CGRID REGULAR 0.0 0.0 0.0 112.0 0.0 500 0
VERTICAL 2
```

The grid resolution is 0.224 m (112m / 500 cells), suitable for modeling waves with periods 4-10 seconds.

## Water Configuration

Controls water properties and wave generation.

| Parameter | Type | Default | Unit | Range | Description |
|-----------|------|---------|------|-------|-------------|
| `water.water_level` | float | 1.0 | m | >0 | Still water level above seafloor |
| `water.water_density` | float | 1000 | kg/m³ | >0 | Water density |
| `water.wave_height` | float | 0.5 | m | >0 | Regular wave height |
| `water.wave_period` | float | 6.0 | s | >0 | Wave period |

### SWASH Mapping

```
SET level={{ water.water_level }}
SET rhowat={{ water.water_density }}
BOUNDCOND SIDE WEST BTYPE WEAKREFL CON REGULAR {{ water.wave_height }} {{ water.wave_period }} 0.0
```

### Usage Notes

- **Water Level**: Measured from the seafloor (z=0). Typical range: 0.5-3.0 m
- **Wave Height**: For regular waves. Use wave heights that satisfy shallow/intermediate water conditions
- **Wave Period**: Affects porosity parameters and simulation duration
- **Water Density**: Standard seawater density is 1025 kg/m³, freshwater is 1000 kg/m³

## Breakwater Configuration

Defines breakwater geometry and properties.

### Control Parameters

| Parameter | Type | Default | Unit | Range | Description |
|-----------|------|---------|------|-------|-------------|
| `breakwater.enable` | bool | true | - | - | Enable/disable breakwater |

### Geometry Parameters

| Parameter | Type | Default | Unit | Range | Description |
|-----------|------|---------|------|-------|-------------|
| `breakwater.crest_height` | float | 2.0 | m | >0 | Height above seafloor |
| `breakwater.crest_length` | float | 2.0 | m | >0 | Length of flat crest |
| `breakwater.slope` | float | 2.0 | - | >0 | Side slope (H:V ratio) |
| `breakwater.breakwater_start_position` | float | 70.0 | m | 0-112 | X-coordinate of breakwater start |

### Material Properties

| Parameter | Type | Default | Unit | Range | Description |
|-----------|------|---------|------|-------|-------------|
| `breakwater.porosity` | float | 0.4 | - | 0-1 | Porosity coefficient |
| `breakwater.stone_density` | float | 2600 | kg/m³ | >0 | Density of armor stones |
| `breakwater.armour_dn50` | float | 1.150 | m | >0 | Median armor stone diameter |

### SWASH Mapping

```
# Porosity model
POROSITY {{ breakwater.armour_dn50 }} {{ breakwater.crest_height }} 200.0 1.1 {{ water.wave_period }}

# Files generated
INPGRID BOTTOM REGULAR 0.0 0.0 0.0 500 0 0.224 0.0 &
  NONSTATIONARY 000000.000 1 SEC {{ simulation_duration }}
READINP BOTTOM 1.0 'bathymetry.txt' 3 0 FREE

INPGRID POROUS REGULAR 0.0 0.0 0.0 500 0 0.224 0.0
READINP POROUS 1.0 'porosity.txt' 3 0 FREE

INPGRID STRUCHEIGHT REGULAR 0.0 0.0 0.0 500 0 0.224 0.0
READINP STRUCHEIGHT 1.0 'structure_height.txt' 3 0 FREE
```

### Usage Notes

- **Crest Height**: Should be appropriate for the water level
- **Slope**: Common values are 1.5-3.0
- **Porosity**: 0.4 is typical for rubble mound structures; 0.0 for impermeable structures
- **Armor DN50**: Should be sized appropriately for wave conditions 

### Computed Properties

The framework automatically calculates:
- **breakwater_end_position**: `start_position + crest_length + 2 * (crest_height * slope)`

## Vegetation Configuration

Optional vegetation modeling on breakwater crest. It should be noted that for now, only the density will vary horizontally and the characteristics of the tallest plant will be used for the whole crest.

### Control Parameters

| Parameter | Type | Default | Unit | Range | Description |
|-----------|------|---------|------|-------|-------------|
| `vegetation.enable` | bool | false | - | - | Enable vegetation modeling |

### Plant Properties (Primary Type)

| Parameter | Type | Default | Unit | Range | Description |
|-----------|------|---------|------|-------|-------------|
| `vegetation.type.plant_height` | float | 0.5 | m | >0 | Height of plants |
| `vegetation.type.plant_diameter` | float | 0.01 | m | >0 | Stem diameter |
| `vegetation.type.plant_density` | float | 1.0 | 1/m² | >0 | Stems per square meter |
| `vegetation.type.drag_coefficient` | float | 1.0 | - | >0 | Drag coefficient |

### Plant Properties (Secondary Type - Optional)

| Parameter | Type | Default | Unit | Range | Description |
|-----------|------|---------|------|-------|-------------|
| `vegetation.other_type.*` | VegetationType | null | - | - | Optional second vegetation type |

### Distribution Parameters

| Parameter | Type | Default | Unit | Range | Description |
|-----------|------|---------|------|-------|-------------|
| `vegetation.distribution` | string | "half" | - | "half", "alternating" | Spatial distribution pattern |
| `vegetation.type_fraction` | float | 0.5 | - | 0-1 | Fraction occupied by primary type |

### SWASH Mapping

```
# Uses the taller vegetation type as base
VEGETATION {{ vegetation.type.plant_height }} {{ vegetation.type.plant_diameter }} 1 {{ vegetation.type.drag_coefficient }}

# Files generated
INPGRID VEGDENSITY REGULAR 0.0 0.0 0.0 500 0 0.224 0.0
READINP VEGDENSITY 1.0 'vegetation_density.txt' 3 0 FREE
```

### Distribution Patterns

- **"half"**: Primary type on seaward half, secondary on leeward half
- **"alternating"**: Alternating strips of each vegetation type

### Usage Notes

- **Plant Height**: Should be reasonable for the water depth and wave heights
- **Plant Density**: Typical values range from 1-1000 stems/m² depending on species
- **Drag Coefficient**: 1.0 is typical for cylindrical vegetation; can vary 0.5-2.0
- **Diameter**: Realistic stem diameters range from 0.005-0.1 m

## Numeric Configuration

Controls simulation timing and output.

### Simulation Control

| Parameter | Type | Default | Unit | Range | Description |
|-----------|------|---------|------|-------|-------------|
| `numeric.n_waves` | int | 50 | - | >0 | Number of wave periods to simulate |

### Wave Gauge Positions

| Parameter | Type | Default | Unit | Range | Description |
|-----------|------|---------|------|-------|-------------|
| `numeric.wave_gauge_positions` | list[float] | [20,60,65,80,100] | m | 0-112 | X-coordinates for wave gauges |

### Fixed Parameters

| Parameter | Value | Unit | Description |
|-----------|--------|------|-------------|
| `numeric.time_step` | 0.05 | s | Initial time step (adaptive) |
| `numeric.output_interval` | 0.1 | s | Output sampling interval |

### SWASH Mapping

```
# Simulation duration
COMPUTE 000000.000 0.05 SEC {{ simulation_duration }}

# Wave gauge points
{% for pos in numeric.wave_gauge_positions %}
POINTS 'WG{{ loop.index }}' {{ pos }} 0.0
{% endfor %}

# Wave gauge outputs
{% for pos in numeric.wave_gauge_positions %}
TABLE 'WG{{ loop.index }}' NOHEADER 'wg{{ loop.index }}.txt' WATL VEL OUT 000000.000 0.1 SEC
{% endfor %}
```

### Computed Properties

- **simulation_duration**: `n_waves * wave_period` (seconds)

### Usage Notes

- **Number of Waves**: 50 waves typically provide stable statistics; use 20+ for preliminary runs
- **Wave Gauges**: Position strategically (incident, transmitted, reflected zones)
- **Time Step**: SWASH automatically adjusts for stability (CFL condition)

## Top-Level Configuration

### Project Settings

| Parameter | Type | Default | Unit | Range | Description |
|-----------|------|---------|------|-------|-------------|
| `name` | string | required | - | - | Experiment name |

### Generated Properties

| Parameter | Type | Description |
|-----------|------|-------------|
| `hash` | string | Configuration hash for reproducibility |
| `*.hash` | string | Section-specific hashes |

## Validation Rules

The framework enforces several validation rules:

1. **Required Fields**: `name` must be specified
2. **Range Constraints**: 
   - `vegetation.type_fraction`: 0.0 ≤ value ≤ 1.0
   - All physical parameters must be positive
3. **Consistency Checks**:
   - Wave gauge positions must be within domain (0-112 m)
   - Breakwater geometry must be physically reasonable

## Configuration Files

### YAML Structure

```yaml
name: "experiment_name"

grid:
  # Fixed parameters only

water:
  water_level: 1.0
  water_density: 1000
  wave_height: 0.5
  wave_period: 6.0

breakwater:
  enable: true
  crest_height: 2.0
  crest_length: 2.0
  slope: 2.0
  porosity: 0.4
  stone_density: 2600
  armour_dn50: 1.150
  breakwater_start_position: 70.0

vegetation:
  enable: false
  type:
    plant_height: 0.5
    plant_diameter: 0.01
    plant_density: 1.0
    drag_coefficient: 1.0
  distribution: "half"
  type_fraction: 0.5

numeric:
  n_waves: 50
  wave_gauge_positions: [20.0, 60.0, 65.0, 80.0, 100.0]
```

### Hash Generation

Each configuration section generates a hash based on all its parameters. This ensures:
- Reproducible simulation directories
- Detection of configuration changes
- Automatic versioning

## Next Steps

- [Template Mapping](template-mapping.md) - Detailed template-to-SWASH mapping
- [SWASH Physics](swash-physics.md) - Understanding the physical model
- [Output Interpretation](output-interpretation.md) - Analyzing simulation results
