# SWASH Commands Quick Reference

## Core Commands Used by Framework

### Model Setup
```
SET level=1.0 grav=9.81 rhowat=1000
MODE NONSTATIONARY ONEDIMENSIONAL
```

### Computational Grid
```
CGRID REGULAR 0.0 0.0 0.0 112.0 0.0 500 0
VERTICAL 2
```

### Input Data Files
```
INPGRID BOTTOM REGULAR 0.0 0.0 0.0 500 0 0.224 1.0
READINP BOTTOM 1.0 'bathymetry.txt' IDLA=3 FREE

INPGRID POROSITY REGULAR 0.0 0.0 0.0 500 0 0.224 1.0  
READINP POROSITY 1.0 'porosity.txt' IDLA=3 FREE

INPGRID HSTRUCTURE REGULAR 0.0 0.0 0.0 500 0 0.224 1.0
READINP HSTRUCTURE 1.0 'structure_height.txt' IDLA=3 FREE

INPGRID NPLANTS REGULAR 0.0 0.0 0.0 500 0 0.224 1.0
READINP NPLANTS 1.0 'vegetation_density.txt' IDLA=3 FREE
```

### Wave Generation
```
BOUNDCOND SIDE WEST BTYPE WEAKREFL CON REGULAR 0.5 6.0 0.0
SPONGE EAST 10.0
```

### Physics Models
```
POROSITY 1.150 2.0 200.0 1.1 6.0
VEGETATION 0.5 0.01 1 1.0
FRICTION MANNING 0.019
BREAKING 0.6 0.3
```

### Numerical Methods
```
NONHYDROSTATIC BOX 1.0
TIMEINT METH EXPLICIT 0.4 0.8
```

### Output Generation
```
POINTS 'WG01' 20.0 0.0
TABLE 'WG01' NOHEADER 'wg01.txt' WATLEV VEL OUTPUT 000000.000 0.1 SEC

QUANTITY HSIG dur=1800 sec
QUANTITY SETUP dur=1800 sec

FRAME 'channel' 0.0 0.0 0.0 112.0 1.0 125 1
BLOCK 'channel' NOHEADER 'final_state.mat' LAY-OUT 3 WATLEV VEL HSIG SETUP OUTPUT 000000.000 0.1 SEC
```

### Execution Control
```
COMPUTE 000000.000 0.05 SEC 300.000
STOP
```

## Command Parameter Mapping

### SET Command
| Parameter | Config Source | Description |
|-----------|---------------|-------------|
| `level` | `water.water_level` | Still water level (m) |
| `rhowat` | `water.water_density` | Water density (kg/m³) |
| `grav` | 9.81 (fixed) | Gravitational acceleration |

### BOUNDCOND Command  
| Parameter | Config Source | Description |
|-----------|---------------|-------------|
| Wave height | `water.wave_height` | Regular wave height (m) |
| Wave period | `water.wave_period` | Wave period (s) |
| Direction | 0.0 (fixed) | Shore-normal waves |

### POROSITY Command
| Parameter | Config Source | Description |
|-----------|---------------|-------------|
| `dn50` | `breakwater.armour_dn50` | Stone diameter (m) |
| `height` | `breakwater.crest_height` | Structure height (m) |
| `A` | 200.0 (fixed) | Drag coefficient |
| `B` | 1.1 (fixed) | Inertia coefficient |
| `T` | `water.wave_period` | Wave period (s) |

### VEGETATION Command
| Parameter | Config Source | Description |
|-----------|---------------|-------------|
| `height` | `vegetation.type.plant_height` | Plant height (m) |
| `diameter` | `vegetation.type.plant_diameter` | Stem diameter (m) |
| `layers` | 1 (fixed) | Number of layers |
| `drag` | `vegetation.type.drag_coefficient` | Drag coefficient |

### POINTS/TABLE Commands
| Parameter | Config Source | Description |
|-----------|---------------|-------------|
| Point names | Auto-generated | WG01, WG02, ... |
| X-positions | `numeric.wave_gauge_positions` | Gauge locations (m) |
| File names | Auto-generated | wg01.txt, wg02.txt, ... |
| Variables | WATLEV VEL (fixed) | Water level and velocity |
| Interval | 0.1 (fixed) | Output interval (s) |

### COMPUTE Command
| Parameter | Config Source | Description |
|-----------|---------------|-------------|
| Start time | 000000.000 (fixed) | Simulation start |
| Time step | 0.05 (fixed) | Initial time step (s) |
| End time | `n_waves × wave_period` | Total duration (s) |

## File Format Specifications

### Grid Specification
```
REGULAR 0.0 0.0 0.0 500 0 0.224 1.0
```
- Origin: (0.0, 0.0)
- Direction: 0.0 (x-direction)
- Grid points: 500
- Spacing: 0.224 m
- Y-direction: 0 (1D)
- Scaling: 1.0

### Data File Format (IDLA=3)
```
READINP BOTTOM 1.0 'bathymetry.txt' IDLA=3 FREE
```
- Scale factor: 1.0
- Format: IDLA=3 (formatted ASCII)
- Terminator: FREE (end-of-record)

## Fixed Parameters

### Numerical Settings
| Parameter | Value | Description |
|-----------|--------|-------------|
| Time integration | EXPLICIT | Explicit scheme |
| CFL range | 0.4-0.8 | Adaptive time stepping |
| Non-hydrostatic | BOX 1.0 | Pressure correction |
| Manning coefficient | 0.019 | Bottom friction |
| Breaking γ | 0.6 | Breaking parameter |
| Breaking α | 0.3 | Dissipation parameter |

### Domain Settings
| Parameter | Value | Description |
|-----------|--------|-------------|
| Length | 112.0 m | Total domain |
| Width | 0.0 | 1D simulation |
| Grid cells | 500 | Spatial resolution |
| Vertical layers | 2 | Vertical discretization |
| Sponge length | 10.0 m | Absorption layer |

### Output Settings
| Parameter | Value | Description |
|-----------|--------|-------------|
| Time interval | 0.1 s | Data sampling |
| Statistics duration | 1800 s | Wave statistics |
| Spatial points | 125 | Final state output |
| File format | ASCII | Human-readable |

## Common Command Combinations

### Basic Wave Simulation
```
SET level=1.0
MODE NONSTATIONARY ONEDIMENSIONAL
CGRID REGULAR 0.0 0.0 0.0 112.0 0.0 500 0
BOUNDCOND SIDE WEST CON REGULAR 0.5 6.0 0.0
COMPUTE 000000.000 0.05 SEC 300.000
```

### With Breakwater
```
INPGRID POROSITY REGULAR 0.0 0.0 0.0 500 0 0.224 1.0
READINP POROSITY 1.0 'porosity.txt' IDLA=3 FREE
POROSITY 1.150 2.0 200.0 1.1 6.0
```

### With Vegetation
```
INPGRID NPLANTS REGULAR 0.0 0.0 0.0 500 0 0.224 1.0
READINP NPLANTS 1.0 'vegetation_density.txt' IDLA=3 FREE
VEGETATION 0.5 0.01 1 1.0
```

### Output Collection
```
POINTS 'WG01' 20.0 0.0
TABLE 'WG01' NOHEADER 'wg01.txt' WATLEV VEL OUTPUT 000000.000 0.1 SEC
QUANTITY HSIG dur=1800 sec
```

## Error-Prone Commands

⚠️ **Common mistakes:**
- Incorrect grid dimensions in INPGRID
- Missing FREE terminator in READINP
- Inconsistent file names between READINP and generated files
- Time format errors in COMPUTE (must be SEC)
- Missing STOP command at end