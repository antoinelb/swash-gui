# Template System and Mapping

This document provides a detailed explanation of how the Jinja2 template system converts YAML configuration parameters into SWASH input files. Understanding this mapping is essential for customizing simulations and troubleshooting issues.

## Template Overview

The framework uses a single Jinja2 template (`templates/INPUT`) that generates the complete SWASH input file based on configuration parameters. The template includes:

- **Conditional sections** for optional features (breakwater, vegetation)
- **Dynamic calculations** for derived parameters
- **Loop constructs** for wave gauge generation
- **Comments** documenting parameter sources

## Template Structure

### Header and Project Setup

```jinja2
$ SWASH Input File - 1D Wave Channel Experiment
$ {{ name }}

PROJECT 'WaveChannel' '{{ project_nr }}'
```

**Mapping:**
- `{{ name }}`: From top-level `name` parameter
- `{{ project_nr }}`: Generated project number

### Model Configuration

```jinja2
SET level={{ water.water_level }} grav=9.81 rhowat={{ water.water_density }}
MODE NONSTATIONARY ONEDIMENSIONAL
```

**Direct Parameter Mapping:**
- `water.water_level` → `level` (still water level in meters)
- `water.water_density` → `rhowat` (water density in kg/m³)
- Fixed: `grav=9.81` (gravitational acceleration)
- Fixed: `NONSTATIONARY ONEDIMENSIONAL` (1D time-dependent mode)

### Computational Grid

```jinja2
CGRID REGULAR 0.0 0.0 0.0 112.0 0.0 500 0
VERTICAL 2
```

**Fixed Parameters:**
- Domain: 0 to 112 m (x-direction)
- Grid cells: 500 (Δx = 0.224 m)
- Vertical layers: 2
- Origin: (0, 0) coordinates

### Bathymetry

```jinja2
INPGRID BOTTOM REGULAR 0.0 0.0 0.0 500 0 0.224 1.0
READINP BOTTOM 1.0 'bathymetry.txt' IDLA=3 FREE
```

**Generated File:** `bathymetry.txt`
- Created by `simulation.py` based on breakwater geometry
- Grid-aligned with computational domain
- IDLA=3: Formatted ASCII data
- FREE: End-of-record marker

## Conditional Sections

### Breakwater Section

```jinja2
{%- if breakwater.enable %}
$=============================================================================
$ BREAKWATER POROSITY
$=============================================================================
{%- set breakwater_end = breakwater.breakwater_start_position + breakwater.crest_length + 2 * (breakwater.crest_height * breakwater.slope) %}
```

**Conditional Logic:**
- Entire section only included if `breakwater.enable=True`
- Calculates `breakwater_end` position dynamically
- Formula: `start + crest_length + 2 × (height × slope)`

**Parameter Mapping:**
```jinja2
INPGRID POROSITY REGULAR 0.0 0.0 0.0 500 0 0.224 1.0
READINP POROSITY 1.0 'porosity.txt' IDLA=3 FREE

INPGRID HSTRUCTURE REGULAR 0.0 0.0 0.0 500 0 0.224 1.0
READINP HSTRUCTURE 1.0 'structure_height.txt' IDLA=3 FREE

POROSITY {{ breakwater.armour_dn50 }} {{ breakwater.crest_height }} 200.0 1.1 {{ water.wave_period }}
```

**Generated Files:**
- `porosity.txt`: Spatial porosity distribution
- `structure_height.txt`: Breakwater geometry profile

**POROSITY Command Parameters:**
1. `breakwater.armour_dn50`: Median stone diameter (m)
2. `breakwater.crest_height`: Structure height (m)
3. `200.0`: Drag coefficient (fixed)
4. `1.1`: Inertia coefficient (fixed)
5. `water.wave_period`: Wave period for Reynolds number calculation

### Vegetation Section

```jinja2
{%- if vegetation.enable and breakwater.enable %}
```

**Double Condition:**
- Vegetation only active when both `vegetation.enable=True` AND `breakwater.enable=True`
- Vegetation requires a breakwater crest for placement

#### Single Vegetation Type

```jinja2
{%- if vegetation.other_type %}
$ Two vegetation types
{%- else %}
$ Single vegetation type on breakwater crest
INPGRID NPLANTS REGULAR 0.0 0.0 0.0 500 0 0.224 1.0
READINP NPLANTS 1.0 'vegetation_density.txt' IDLA=3 FREE
VEGETATION {{ vegetation.type.plant_height }} {{ vegetation.type.plant_diameter }} 1 {{ vegetation.type.drag_coefficient }}
{%- endif %}
```

**VEGETATION Command Parameters:**
1. `vegetation.type.plant_height`: Plant height (m)
2. `vegetation.type.plant_diameter`: Stem diameter (m)
3. `1`: Number of vegetation layers (fixed)
4. `vegetation.type.drag_coefficient`: Drag coefficient

#### Dual Vegetation Types

```jinja2
{%- if vegetation.type.plant_height >= vegetation.other_type.plant_height %}
VEGETATION {{ vegetation.type.plant_height }} {{ vegetation.type.plant_diameter }} 1 {{ vegetation.type.drag_coefficient }}
{%- else %}
VEGETATION {{ vegetation.other_type.plant_height }} {{ vegetation.other_type.plant_diameter }} 1 {{ vegetation.other_type.drag_coefficient }}
{%- endif %}
```

**Logic:**
- Uses the **taller** vegetation type for the VEGETATION command
- SWASH requires a single vegetation definition but reads density from file
- Spatial distribution handled in `vegetation_density.txt`

## Wave Generation

```jinja2
BOUNDCOND SIDE WEST BTYPE WEAKREFL &
          CON REGULAR {{ water.wave_height }} {{ water.wave_period }} 0.0

SPONGE EAST 10.0
```

**Parameter Mapping:**
- `water.wave_height`: Wave height (m)
- `water.wave_period`: Wave period (s)
- `0.0`: Wave direction (shore-normal, fixed)
- `WEAKREFL`: Weakly reflective boundary
- `SPONGE EAST 10.0`: 10m absorption layer at downstream end

## Physics Configuration

### Bottom Friction

```jinja2
FRICTION MANNING 0.019
```

**Fixed Parameter:**
- Manning coefficient n = 0.019 (typical for sand/gravel)

### Wave Breaking

```jinja2
BREAKING 0.6 0.3
```

**Fixed Parameters:**
- γ = 0.6: Breaking parameter (H/h ratio)
- α = 0.3: Dissipation parameter

### Numerical Schemes

```jinja2
NONHYDROSTATIC BOX 1.0
TIMEINT METH EXPLICIT 0.4 0.8
```

**Fixed Parameters:**
- BOX scheme for non-hydrostatic pressure
- Explicit time integration
- CFL range: 0.4-0.8 (adaptive)

## Output Generation

### Wave Gauge Points

```jinja2
{%- for i, pos in enumerate(numeric.wave_gauge_positions) %}
POINTS 'WG{{ "%02d"|format(i+1) }}' {{ pos }} 0.0
{%- endfor %}
```

**Loop Logic:**
- Iterates through `numeric.wave_gauge_positions` list
- Creates points WG01, WG02, WG03, etc.
- Format: `"%02d"` ensures zero-padding (01, 02, 03...)

**Generated Output:**
```
POINTS 'WG01' 20.0 0.0
POINTS 'WG02' 60.0 0.0
POINTS 'WG03' 65.0 0.0
```

### Time Series Output

```jinja2
{%- for i, pos in enumerate(numeric.wave_gauge_positions) %}
TABLE 'WG{{ "%02d"|format(i+1) }}' NOHEADER 'wg{{ "%02d"|format(i+1) }}.txt' &
      WATLEV VEL OUTPUT 000000.000 0.1 SEC
{%- endfor %}
```

**Output Files:**
- `wg01.txt`, `wg02.txt`, etc.
- Contains: water level (WATLEV) and velocity (VEL)
- Sampling: Every 0.1 seconds
- NOHEADER: No column headers in output

### Spatial Output

```jinja2
FRAME 'channel' 0.0 0.0 0.0 112.0 1.0 125 1
BLOCK 'channel' NOHEADER 'final_state.mat' LAY-OUT 3 &
      WATLEV VEL HSIG SETUP OUTPUT 000000.000 0.1 SEC
```

**Final State Output:**
- File: `final_state.mat`
- Variables: water level, velocity, significant wave height, setup
- Grid: 125 points across domain
- Format: LAY-OUT 3 (formatted ASCII)

## Simulation Control

```jinja2
COMPUTE 000000.000 0.05 SEC {{ "%010.3f"|format(simulation_duration) }}
```

**Parameter Calculation:**
- `simulation_duration = numeric.n_waves × water.wave_period`
- Initial time step: 0.05 seconds
- Format: `"%010.3f"` ensures 10-digit format with 3 decimals

## File Generation Process

### Template Rendering

1. **Load Configuration**: Parse YAML into Pydantic models
2. **Calculate Properties**: Compute derived values (durations, positions)
3. **Render Template**: Apply Jinja2 with configuration context
4. **Generate Auxiliary Files**: Create bathymetry, porosity, vegetation files
5. **Write INPUT File**: Save rendered template

### Auxiliary File Generation

The template references several generated files:

| File | Condition | Content | Generator |
|------|-----------|---------|-----------|
| `bathymetry.txt` | Always | Seafloor elevation | `simulation.py` |
| `porosity.txt` | `breakwater.enable` | Porosity distribution | `simulation.py` |
| `structure_height.txt` | `breakwater.enable` | Structure height | `simulation.py` |
| `vegetation_density.txt` | `vegetation.enable` | Plant density | `simulation.py` |

## Template Customization

### Adding Parameters

To add new configuration parameters:

1. **Update Config Model**: Add field to appropriate Pydantic model
2. **Modify Template**: Use `{{ section.parameter }}` syntax
3. **Update Documentation**: Document new parameter
4. **Test Validation**: Ensure parameter validation works

### Conditional Features

To add new conditional features:

```jinja2
{%- if new_feature.enable %}
$ New feature section
NEW_COMMAND {{ new_feature.parameter }}
{%- endif %}
```

### Advanced Logic

For complex parameter relationships:

```jinja2
{%- set calculated_value = parameter1 * parameter2 + parameter3 %}
$ Calculated value: {{ calculated_value }}
COMMAND {{ calculated_value }}
```

## Debugging Templates

### Common Issues

1. **Missing Parameters**: Check parameter paths match config structure
2. **Conditional Logic**: Verify boolean conditions
3. **Format Strings**: Ensure numeric formatting is correct
4. **Loop Variables**: Check enumerate() usage for indexed loops

### Testing Templates

```python
from jinja2 import Template
template = Template(open('templates/INPUT').read())
output = template.render(config_dict)
print(output)
```

## Next Steps

- [Configuration Reference](configuration-reference.md) - Complete parameter documentation
- [Output Interpretation](output-interpretation.md) - Understanding simulation results
- [Troubleshooting Guide](troubleshooting-guide.md) - Common issues and solutions