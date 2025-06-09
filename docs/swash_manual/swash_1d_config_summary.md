# SWASH 1D Wave Channel Configuration: Breakwater with Vegetation

## Overview
This summary details the SWASH parameters required to configure a 1D wave channel containing a breakwater with two different vegetation characteristics on top. The configuration involves several key components: 1D mode setup, breakwater representation through porosity layers, and vegetation characteristics.

## 1. Basic 1D Mode Configuration

### MODE Command
```
MODE NONSTATIONARY ONEDIMENSIONAL
```
- **NONSTATIONARY**: Required keyword for time-dependent simulations
- **ONEDIMENSIONAL**: Specifies 1D mode (flume-like) instead of 2D (basin-like)
- Sets ∂/∂y ≡ 0 (no variation in y-direction)

### Computational Grid (CGRID)
```
CGRID REGULAR [xpc] [ypc] [alpc] [xlenc] [ylenc] [mxc] [myc]
```
**1D-specific parameters:**
- `[ylenc]`: Should be 0 for 1D mode
- `[myc]`: Should be 0 for 1D mode
- `[alpc]`: Should equal `[alpinp]` (input grid direction)
- `[mxc]`: Number of meshes in x-direction (one less than grid points)
- `[xlenc]`: Length of computational domain in x-direction

## 2. Breakwater Configuration (Porosity Layers)

### POROSITY Command
```
POROSITY [size] [height] [alpha0] [beta0] [wper]
```

**Parameters:**
- `[size]`: Characteristic grain size of porous structure (metres)
  - Typical armour layer: 0.5 m
  - Can vary spatially using INPGRID PSIZE and READINP PSIZE
- `[height]`: Structure height relative to bottom (metres)
  - Default: 99999 (emerged structure)
  - Can vary spatially using INPGRID HSTRUCTURE and READINP HSTRUCTURE
- `[alpha0]`: Dimensionless constant for laminar friction loss (surface friction)
  - Default: 200
- `[beta0]`: Dimensionless constant for turbulent friction loss (form drag)
  - Default: 1.1
- `[wper]`: Characteristic wave period (seconds)
  - Required for wave-structure interaction

### Porosity Input Grid Configuration
```
INPGRID POROSITY REGULAR [xpinp] [ypinp] [alpinp] [mxinp] [myinp] [dxinp] [dyinp]
```
**1D-specific:**
- `[myinp]`: Should be 0 for 1D mode
- `[dyinp]`: Can have any value in 1D mode

### Reading Porosity Data
```
READINP POROSITY [fac] 'fname' [idla] [nhedf] [nhedt] [nhedvec]
```
**Porosity values:**
- **1.0**: Water points
- **0.4**: Typical rubble mound breakwater
- **< 0.1**: Impermeable regions (treated as land points)

**Design considerations:**
- Breakwater width should be ≥ 4 × grid size
- Typical porosity for breakwaters: n = 0.4
- Stone size for armour layer: typically 0.5 m

## 3. Vegetation Configuration

### VEGETATION Command
```
VEGETATION < [height] [diamtr] [nstems] [drag] > INERTIA [cm] POROSITY VERTICAL
```

**Basic parameters (repeatable for multiple vertical segments):**
- `[height]`: Plant height per vertical segment (metres)
- `[diamtr]`: Diameter of each plant stand per segment (metres)
- `[nstems]`: Number of plant stands per square metre
  - Default: 1
  - Can vary horizontally using INPGRID NPLANTS and READINP NPLANTS
- `[drag]`: Drag coefficient per vertical segment

**Optional enhancements:**
- **INERTIA `[cm]`**: Includes inertia force
  - `[cm]`: Added mass coefficient
- **POROSITY**: Includes porosity effect for dense vegetation
- **VERTICAL**: Includes drag force in vertical direction

### Vegetation Input Grid
```
INPGRID NPLANTS REGULAR [xpinp] [ypinp] [alpinp] [mxinp] [myinp] [dxinp] [dyinp]
```

### Reading Vegetation Data
```
READINP NPLANTS [fac] 'fname' [idla] [nhedf]
```
- Reads horizontally varying vegetation density (per m²)
- Multiplied with vertically varying values from VEGETATION command

## 4. Two Different Vegetation Characteristics

To implement two different vegetation types on the breakwater:

### Approach 1: Vertical Segmentation
```
VEGETATION [height1] [diamtr1] [nstems1] [drag1] [height2] [diamtr2] [nstems2] [drag2]
```
- Define multiple vertical segments with different characteristics
- Each segment represents different vegetation properties

### Approach 2: Spatial Variation
```
INPGRID NPLANTS REGULAR [parameters]
READINP NPLANTS [fac] 'vegetation_density_file'
```
- Use input grid to define spatially varying vegetation density
- Combine with VEGETATION command for different characteristics

## 5. Boundary Conditions for 1D Channel

### Wave Generation Boundary
```
BOUNDCOND SIDE WEST BTYPE WEAKREFL REGULAR [h] [per] [dir]
```
or
```
BOUNDCOND SIDE WEST BTYPE WEAKREFL SPECTRUM [h] [per] [dir] [dd] [cycle] SEC
```

**1D-specific considerations:**
- Use SIDE WEST/EAST for 1D boundaries
- WEAKREFL recommended for wave generation to allow outgoing waves
- REGULAR for monochromatic waves
- SPECTRUM for irregular waves

### Absorbing Boundary
```
SPONGELAYER EAST [width]
```
or
```
BOUNDCOND SIDE EAST BTYPE SOMMERFELD
```

## 6. Physical Parameters

### Bottom Friction
```
FRICTION MANNING [cf]
```
- Recommended Manning coefficient: 0.019 for wave simulations
- Important for long-distance wave propagation

### Non-hydrostatic Pressure
```
NONHYDROSTATIC BOX [theta]
```
- BOX scheme recommended for wave simulations with ≤ 5 layers
- `[theta]`: Default 1.0 for stability

### Vertical Layers
```
VERTICAL [kmax] < [thickness] PERC >
```
- For waves: 1-3 equidistant layers usually sufficient
- For flow structures: ≥ 10 layers recommended

## 7. Time Integration and Stability

### Time Step Control
```
TIMEI METH EXPL [cfllow] [cflhig]
```
- `[cfllow]`: Minimum Courant number (default: 0.4)
- `[cflhig]`: Maximum Courant number (default: 0.8)
- For high waves/structures: use Courant ≤ 0.5

### Computation Control
```
COMPUTE [tbegc] [deltc] SEC [tendc]
```

## 8. Output Configuration

### Output Locations
```
POINTS 'channel_points' < [xp] [yp] >
```

### Output Variables
```
TABLE 'channel_points' HEADER 'output_file.dat' WATLEV VEL VMAG
```

## Example Configuration Structure

```
PROJECT 'Wave Channel' '001'
        'Breakwater with vegetation'

MODE NONSTATIONARY ONEDIMENSIONAL

CGRID REGULAR 0.0 0.0 0.0 100.0 0.0 500 0

VERTICAL 2 50 PERC 50 PERC

INPGRID BOTTOM REGULAR 0.0 0.0 0.0 500 0 0.2 1.0
READINP BOTTOM 1.0 'bottom.dat'

INPGRID POROSITY REGULAR 0.0 0.0 0.0 500 0 0.2 1.0
READINP POROSITY 1.0 'porosity.dat'

POROSITY 0.5 5.0 200 1.1 8.0

VEGETATION 2.0 0.05 100 1.0 1.0 0.02 200 0.8 INERTIA 1.0

BOUNDCOND SIDE WEST BTYPE WEAKREFL REGULAR 1.0 8.0 0.0

SPONGELAYER EAST 20.0

NONHYDROSTATIC BOX 1.0

FRICTION MANNING 0.019

COMPUTE 0.0 0.05 SEC 100.0

STOP
```

## Key Considerations

1. **Grid Resolution**: Minimum 15-20 cells per wavelength in shallow areas
2. **Breakwater Width**: At least 4 times the grid size
3. **Vegetation Segments**: Can define multiple vertical segments for varying characteristics
4. **Time Step**: Courant number ≤ 0.5 for stability with structures
5. **Spin-up Time**: Allow 10-15% of total simulation for model stabilization
6. **1D Limitations**: No y-direction variation, straight boundaries only