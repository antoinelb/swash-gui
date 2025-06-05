# Breakwater Design and Physical Structure

## Overview

This document describes the physical breakwater structure modeled in the SWASH framework. The design is based on living breakwaters proposed for Baie-des-Bacon, Québec, featuring a rubble mound structure with vegetation on the crest for enhanced wave attenuation and ecological benefits.

## Breakwater Geometry

### Cross-Sectional Profile

The breakwater has a **trapezoidal cross-section** with the following key dimensions:

```
                     |<-- crest_width -->|
                     |                   |
    SWL -------------|------- - - - - ---|----------- 
                    /|                   |\
                   / |                   | \
                  /  |   crest_height    |  \
                 /   |                   |   \
                /    |                   |    \
    ___________/     |___________________|     \___________
    |<-- slope -->|  |                   |  |<-- slope -->|
       (1.75:1)                                 (1.75:1)

    ^-- breakwater_start_position
                                        ^-- breakwater_end_position
```

### Geometric Parameters

| Parameter | Default Value | Units | Description |
|-----------|---------------|-------|-------------|
| `crest_height` | 2.0 | m | Height of breakwater crest above the bottom |
| `crest_width` | 3.0 | m | Width of the flat crest section |
| `slope` | 1.75 | H:V | Slope of breakwater sides (horizontal:vertical ratio) |
| `breakwater_start_position` | 100.0 | m | X-coordinate where breakwater begins |

### Calculated Dimensions

The framework automatically calculates:

- **Breakwater end position**: `start_position + crest_width + 2 × (crest_height × slope)`
- **Total base width**: `crest_width + 2 × (crest_height × slope)` 
- **Side slope length**: `crest_height × √(1 + slope²)`

For the default parameters:
- Breakwater end position: 100.0 + 3.0 + 2 × (2.0 × 1.75) = **110.0 m**
- Total base width: 3.0 + 2 × (2.0 × 1.75) = **10.0 m**
- Side slope length: 2.0 × √(1 + 1.75²) = **4.06 m**

## Material Properties

### Armour Stone Characteristics

The breakwater consists of different stone classes with specified properties:

| Stone Type | Parameter | Default Value | Units | Description |
|------------|-----------|---------------|-------|-------------|
| **Armour** | `armour_dn50` | 1.15 | m | Median diameter of armour stones |
| **Filter** | `filter_dn50` | 0.5 | m | Median diameter of filter layer stones |
| **Core** | `core_dn50` | 0.2 | m | Median diameter of core stones |

### Stone and Water Properties

| Property | Parameter | Default Value | Units | Description |
|----------|-----------|---------------|-------|-------------|
| Stone density | `stone_density` | 2600 | kg/m³ | Density of rock material |
| Water density | `water_density` | 1000 | kg/m³ | Density of water |
| Porosity | `porosity` | 0.4 | - | Void fraction in breakwater structure |

### Physical Significance

- **Dn50**: The median stone diameter where 50% of stones (by weight) are smaller
- **Porosity**: Fraction of void space in the rock structure, affects wave transmission
- **Density ratio**: Δ = (ρs - ρw)/ρw = (2600 - 1000)/1000 = **1.6** (relative buoyant density)

## Vegetation Design

### Vegetation Characteristics

When vegetation is enabled (`vegetation.enable: true`), the following parameters control the plant properties:

| Parameter | Default Value | Units | Description |
|-----------|---------------|-------|-------------|
| `plant_height` | 0.5 | m | Height of vegetation above crest |
| `plant_diameter` | 0.01 | m | Effective diameter of plant stems |
| `plant_density` | 10 | stems/m² | Number of plant stems per unit area |
| `drag_coefficient` | 1.0 | - | Drag coefficient for vegetation |

### Vegetation Placement

- **Location**: Vegetation is applied **only on the breakwater crest** through spatial density distribution
- **Crest calculation**: Vegetation zone = breakwater extent minus side slopes
- **Spatial file**: `vegetation_density.dat` contains plant density at each grid point
- **Seasonal variation**: Can be modeled by adjusting `plant_density` and `drag_coefficient`

### Physical Considerations

The vegetation parameters are based on:

- **Coastal plant species** typical of the Québec shoreline (e.g., Rosa rugosa, Alnus viridis)
- **Realistic stem densities** for mature vegetation communities
- **Literature values** for vegetation drag coefficients
- **Seasonal variations** (summer vs. winter foliage conditions)

## Hydraulic Design Conditions

### Water Levels

The framework supports various water level scenarios:

| Scenario | Water Level | Wave Height | Description |
|----------|-------------|-------------|-------------|
| Storm (overload) | 3.6 m | 2.4 m | 1/100 year event + sea level rise |
| Storm (design) | 3.6 m | 1.5 m | 12 hrs/year frequency |
| Storm (typical) | 2.7 m | 1.5 m | Current conditions |
| Average | 1.6 m | 1.0 m | Normal operating conditions |

### Wave Conditions

Regular waves are used for systematic analysis:

| Parameter | Typical Range | Units | Description |
|-----------|---------------|-------|-------------|
| Wave height | 0.5 - 2.4 | m | Depends on scenario |
| Wave period | 3 - 12 | s | Covers typical storm conditions |
| Wave length | 13 - 70 | m | Calculated from period and depth |

## Structure Performance Characteristics

### Low-Crested Behavior

Under most design conditions, the breakwater operates as a **low-crested structure**:

- **Negative freeboard**: Water level often above crest elevation
- **Wave overtopping**: Significant water volumes pass over the structure
- **Wave transmission**: Partial wave energy passes through and over
- **Flow acceleration**: High velocities over the crest during wave passage

### Design Functions

The breakwater is designed to:

1. **Attenuate wave energy** through:
   - Porous media effects in the stone structure
   - Form drag from vegetation on the crest
   - Wave breaking and energy dissipation

2. **Limit overtopping discharge** to acceptable levels for:
   - Shoreline protection behind the structure
   - Maintenance of coastal ecosystems
   - Recreational use of protected areas

3. **Provide ecological benefits** through:
   - Habitat creation on the structure crest
   - Reduced wave action in protected areas
   - Enhanced sediment stability

## Model Representations

### SWASH Implementation

The physical structure is represented in SWASH through:

#### 1. Bathymetry (`bathymetry.dat`)
- **Flat bottom** at z = 0.0 for controlled conditions
- **Regular grid spacing** of ~0.224 m (112 m / 500 cells)
- **1D profile** representing cross-shore transect

#### 2. Structure Height (`structure_height.dat`)
- **Height field** defining the top of porous structure
- **Zero outside breakwater**, `crest_height` within breakwater extent
- **Used by SWASH** to determine porous media boundaries

#### 3. Porosity Field (`porosity.dat`)  
- **Porosity values** defining void fraction in each cell
- **Zero in water**, `porosity` value within breakwater
- **Controls flow resistance** and wave transmission

#### 4. Vegetation Drag
- **Spatial application** via `vegetation_density.dat` file
- **Crest-only placement** calculated from breakwater geometry
- **Drag force calculation** based on flow velocity and vegetation properties
- **Energy dissipation** through form drag on plant stems

### Physical Scaling

The model can represent:
- **Laboratory scale**: Direct modeling of wave channel experiments
- **Prototype scale**: Full-scale field conditions
- **Scaled experiments**: Using Froude scaling laws for physical model studies

## Design Validation

### Key Performance Metrics

The breakwater design is evaluated based on:

1. **Transmission coefficient** (Kt): Ratio of transmitted to incident wave height
2. **Overtopping discharge** (q): Volume flow rate per unit width over crest
3. **Wave setup**: Mean water level increase behind structure
4. **Vegetation survival**: Structural integrity under wave loading

### Optimization Parameters

Key parameters for design optimization:

- **Crest elevation**: Balancing protection level with ecological function
- **Structure width**: Affecting wave transmission and material costs
- **Porosity**: Controlling flow through structure
- **Vegetation density**: Optimizing additional energy dissipation

## Next Steps

For detailed information on configuring these parameters, see:
- [Configuration Guide](configuration-guide.md) - Setting up simulation parameters
- [Physics and Parameters](physics-and-parameters.md) - Understanding the physical meaning
- [Input File Reference](input-file-reference.md) - SWASH implementation details