# Output Interpretation

This document explains how to understand and interpret SWASH simulation outputs, including file formats, data structures, and physical meaning of results.

## Output File Overview

Each simulation creates a structured directory with SWASH outputs and processed analysis files:

```
simulations/experiment_name_hash/
├── config.yml              # Copy of configuration
├── swash/                  # SWASH working directory
│   ├── INPUT               # Generated SWASH input file
│   ├── PRINT               # SWASH execution log
│   ├── Errfile             # SWASH errors (if any)
│   ├── bathymetry.txt      # Bottom elevation data
│   ├── porosity.txt        # Breakwater porosity (if enabled)
│   ├── structure_height.txt # Breakwater geometry (if enabled) 
│   ├── vegetation_density.txt # Plant density (if enabled)
│   ├── wg01.txt, wg02.txt, ... # Wave gauge time series
│   ├── data.csv            # Consolidated wave gauge data
│   └── final_state.mat     # Final spatial state
└── analysis/               # Post-processed results
    ├── water_levels_and_x_velocity.png # Visualization
    └── water_levels_and_x_velocity.json # Visualization data for dashboard
```

## Primary Output Files

### Wave Gauge Time Series (wgXX.txt)

**Purpose:** Time series of water levels and velocities at specific locations

**Format:** Space-separated ASCII values, no headers
```
0.1245  0.0234  0.0000
0.1367  0.0189  0.0000
0.1421  0.0145  0.0000
...
```

**Columns:**
1. **Water Level (m)**: Surface elevation relative to still water level
2. **X-Velocity (m/s)**: Horizontal velocity component
3. **Y-Velocity (m/s)**: Cross-shore velocity (always 0 in 1D)

**Timing:** Each row represents one output timestep (default: 0.1 second intervals)

**Physical Interpretation:**
- **Positive water levels**: Waves above still water level
- **Negative water levels**: Wave troughs below still water level
- **Velocity patterns**: Show orbital motion and mean flow components
- **Phase relationships**: Velocity leads water level by 90° in progressive waves

### Final State File (final_state.mat)

**Purpose:** Spatial distribution of wave statistics and final conditions

**Format:** MATLAB binary format with structured data

**Variables:**
- **Watlev**: Water surface elevation at final timestep (m)
- **vel_x**: Horizontal velocity at final timestep (m/s)
- **vel_y**: Cross-shore velocity (zeros for 1D) (m/s)
- **Hsig**: Significant wave height distribution (m)
- **Setup**: Wave-induced mean water level change (m)

**Spatial Grid:** 125 points across 112m domain ($\Delta x \approx 0.9$m)

**Physical Interpretation:**
- **Hsig**: Root-mean-square wave height × 2 (approximates $H_{1/3}$)
- **Setup**: Positive values indicate water level rise due to wave stress
- **Spatial patterns**: Show wave transformation across the domain

### Input Data Files

#### Bathymetry (bathymetry.txt)

**Content:** Bottom elevation at each grid point
```
-1.0000
-1.0000
-0.9500  # Breakwater ramp
 0.5000  # Breakwater crest
-1.0000  # Return to seabed
...
```

**Grid:** 501 points (computational grid resolution)
**Units:** Elevation in meters (negative below datum)

#### Porosity (porosity.txt)

**Content:** Porosity coefficient for each grid cell
```
1.0000  # Water (no structure)
1.0000
0.4000  # Breakwater region
0.4000
1.0000  # Water again
...
```

**Values:** 0.0 (solid/water) to 1.0 (fully porous)

#### Structure Height (structure_height.txt)

**Content:** Breakwater height above bottom
```
0.0000  # No structure
0.0000
2.0000  # Breakwater crest height
1.5000  # Sloping sides
0.0000  # No structure
...
```

**Units:** Height in meters above local bottom

#### Vegetation Density (vegetation_density.txt)

**Content:** Plant stem density distribution
```
0.0000  # No vegetation
0.0000
1.0000  # Primary vegetation density
0.5000  # Secondary vegetation density
0.0000  # No vegetation
...
```

**Units:** Stems per square meter

## Analysis Module Outputs

### Consolidated Data (data.csv)

**Purpose:** Combined wave gauge data with metadata

**Format:** CSV with headers
```csv
timestep,water_level,x_velocity,y_velocity,position
0.0,0.1245,0.0234,0.0,20.0
0.1,0.1367,0.0189,0.0,20.0
...
```

**Columns:**
- **timestep**: Time in seconds from simulation start
- **water_level**: Surface elevation (m)
- **x_velocity**: Horizontal velocity (m/s)
- **y_velocity**: Cross-shore velocity (always 0)
- **position**: X-coordinate of wave gauge (m)

### Visualization (PNG/JSON)

**Statistical Box Plots:**
- **Water Levels**: Distribution of surface elevations at each gauge
- **X-Velocities**: Distribution of horizontal velocities at each gauge
- **Quartiles**: Show median, 25th/75th percentiles, outliers
- **Breakwater Overlay**: Gray shading indicates structure location

**Data to be rendered by plotly.js in dashboard (JSON):**
- Zoom and pan capabilities
- Hover tooltips with exact values
- Toggle data series on/off

## Wave Statistics

### Currently Available

**Time Series Statistics:**
- Quartile distributions at each wave gauge
- Extreme value identification
- Temporal averaging effects

**Spatial Statistics (from SWASH):**
- $H_{sig}$: Significant wave height distribution
- Setup: Mean water level changes

### Traditional Coastal Engineering Metrics

**Wave Heights (not currently calculated):**
- **$H_{1/3}$**: Significant wave height (average of highest 1/3 waves)
- **$H_{rms}$**: Root-mean-square wave height
- **$H_{max}$**: Maximum individual wave height

**Wave Periods (not currently calculated):**
- **$T_p$**: Peak period from spectral analysis
- **$T_z$**: Zero-crossing period
- **$T_{1/3}$**: Period of significant waves

**Transformation Coefficients (not currently calculated):**
- **$K_t$**: Transmission coefficient (transmitted/incident energy)
- **$K_r$**: Reflection coefficient (reflected/incident energy)
- **$K_d$**: Dissipation coefficient ($1 - K_t - K_r$)

## Troubleshooting Output Issues

### Common Problems

**Missing Wave Gauge Files:**
- Check wave gauge positions are within domain (0-112m)
- Verify SWASH completed successfully (check PRINT file)

**Irregular Time Series:**
- May indicate numerical instability
- Check CFL condition and time step size
- Review PRINT file for warnings

**Unexpected Wave Heights:**
- Verify boundary conditions match configuration
- Check for wave breaking (height/depth ratios)
- Review grid resolution adequacy

**Zero Velocities:**
- May indicate model not reaching steady state
- Increase number of wave periods (n_waves)
- Check vegetation/porosity parameters

### Quality Checks

**Mass Conservation:**
- Time-averaged flow should be minimal
- Large mean velocities indicate setup problems

**Energy Conservation:**
- Total energy should decrease gradually due to dissipation
- Sudden energy changes indicate numerical issues

**Physical Realism:**
- Wave heights should be reasonable for water depth
- Velocities should be proportional to wave steepness

## Advanced Analysis Possibilities

### Spectral Analysis

**Power Spectral Density:**
- Identify dominant frequencies
- Quantify harmonic generation
- Analyze frequency-dependent dissipation

### Wave Breaking Analysis

**Breaking Criteria:**
- Monitor height-to-depth ratios
- Identify breaking locations
- Quantify energy dissipation rates

### Setup and Runup

**Mean Water Level:**
- Calculate wave setup from time-averaged levels
- Analyze spatial gradients
- Compare with analytical predictions

### Structure Performance

**Overtopping Analysis:**
- Calculate overtopping rates and volumes
- Analyze extreme events
- Assess structure effectiveness

## Next Steps

- [Troubleshooting Guide](troubleshooting-guide.md) - Common issues and solutions
- [Configuration Reference](configuration-reference.md) - Parameter documentation
- [SWASH Physics](swash-physics.md) - Understanding the numerical model
