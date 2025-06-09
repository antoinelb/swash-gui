# Experiments and Model Configurations

This document describes the experimental configurations available in this SWASH simulation framework, their purposes, and their parameters.

## Overview

The experiments in this repository are designed to study the hydrodynamic behavior of vegetated breakwaters using SWASH 1D wave channel simulations. Each configuration represents a specific research scenario with carefully chosen parameters for physical accuracy and computational efficiency.

## Configuration Naming Convention

- `dev.yml`: Development and testing configuration with fast execution
- `model001.yml`: Primary research configuration for vegetated breakwater studies
- `test_*.yml`: Quick validation configurations
- `two_vegetation_types.yml`: Demonstration of dual vegetation implementation

## Experiment Configurations

### model001.yml - Vegetated Breakwater Research Model

**Purpose**: Primary research configuration for studying wave-vegetation-structure interactions on low-crested breakwaters with realistic physical parameters.

**Physical Configuration**:
- **Domain**: 112m wave channel
- **Breakwater**:
  - Location: 70.0m from wave generation boundary
  - Crest height: 0.917m (relative to bottom)
  - Crest width: 1.376m
  - Side slopes: 1.75:1 (H:V)
  - Porosity: 0.4 (typical rubble mound)
  - Armour stone Dn50: 0.393m
  - Stone density: 2700 kg/m³

- **Water Conditions**:
  - Still water level: 1.65m
  - Wave height: 1.1m (significant wave forcing)
  - Wave period: 8.0s (typical storm waves)
  - Water density: 1000 kg/m³

- **Vegetation**:
  - Type: Single vegetation type on crest
  - Height: 0.5m above crest
  - Diameter: 0.02m (typical coastal vegetation stems)
  - Density: 50 stems/m²
  - Drag coefficient: 1.2

**Numerical Configuration**:
- **Grid**: 560 cells (0.2m resolution, ~18 cells per wavelength)
- **Vertical layers**: 2 (optimal for wave simulations)
- **Time integration**: 
  - Initial time step: 0.03s (Courant ≤ 0.5 for stability)
  - Adaptive time stepping enabled
- **Simulation duration**: 1000 waves (8000s total)
- **Output frequency**: 0.2s (T/40 for detailed wave analysis)

**Wave Gauge Locations**:
- 20.0m: Incident wave measurement
- 30.0m: Pre-breakwater conditions  
- 70.0m: At breakwater toe (seaward side)
- 72.3m: Within breakwater structure
- 74.6m: At breakwater crest
- 80.0m: Transmitted wave measurement

**Research Applications**:
- Wave energy dissipation by vegetation
- Overtopping reduction effectiveness
- Vegetation survival under wave loading
- Structure-vegetation interaction dynamics
- Comparison with unvegetated breakwater performance

**Computational Efficiency**:
- **Optimized parameters** based on SWASH manual recommendations:
  - Grid resolution: 15-20 cells per wavelength (18 achieved)
  - Breakwater width: >4× grid size (6.9× achieved)
  - Time step: Courant ≤ 0.5 for structures
  - Output frequency: T/40 for wave analysis
- **Expected runtime**: ~2-3 hours on modern hardware
- **Output size**: ~500MB for full simulation

**Validation Notes**:
- Freeboard: 0.55m (crest above water level)
- Relative crest height: Hc/H = 0.917/1.1 = 0.83 (overtopped structure)
- Wave steepness: H/L ≈ 0.02 (moderate steepness)
- Breakwater width: 7× significant wave height

### dev.yml - Development Configuration

**Purpose**: Fast-executing configuration for development, testing, and debugging.

**Key Parameters**:
- Grid: 500 cells (0.224m resolution)
- Simulation: 50 waves (250s duration)  
- Wave conditions: H=0.6m, T=5.0s
- Vegetation: Dual vegetation types enabled
- Expected runtime: ~30 seconds

**Use Cases**:
- Code development and testing
- Parameter sensitivity studies
- Dashboard development
- CI/CD validation

### two_vegetation_types.yml - Dual Vegetation Demonstration

**Purpose**: Demonstrates the implementation of two different vegetation types on a single breakwater crest.

**Key Features**:
- **Primary vegetation**: Dense shrubs (50 stems/m², 0.5m height)
- **Secondary vegetation**: Tall grasses (200 stems/m², 1.0m height)
- **Distribution**: Half-and-half across crest width
- **Research focus**: Spatial heterogeneity effects

## Design Considerations

### Grid Resolution Guidelines
- **Minimum**: 15 cells per wavelength in shallow water
- **Optimal**: 18-20 cells per wavelength
- **Breakwater constraint**: Width ≥ 4× grid cell size

### Time Step Stability
- **Waves only**: Courant number ≤ 0.8
- **With structures**: Courant number ≤ 0.5
- **With vegetation**: Consider plant flexibility effects

### Simulation Duration
- **Spin-up time**: 10-15% of total simulation
- **Statistical analysis**: 200-300 waves minimum
- **Detailed studies**: 500-1000 waves

### Output Configuration
- **Wave analysis**: T/40 to T/80 temporal resolution
- **Overtopping studies**: T/100 or higher resolution
- **Long-term statistics**: T/10 acceptable

## Experimental Methodology

### Standard Workflow
1. **Configuration setup**: Select appropriate experiment file
2. **Pre-processing**: Validate grid resolution and stability criteria
3. **Execution**: Run simulation with progress monitoring
4. **Post-processing**: Analyze wave statistics and vegetation effects
5. **Validation**: Compare against physical model data or analytical solutions

### Performance Optimization
- Use `dev.yml` for initial parameter exploration
- Scale to full resolution (`model001.yml`) for final results
- Monitor Courant number warnings during execution
- Adjust output frequency based on analysis needs

### Quality Assurance
- Verify spin-up period completion before analysis
- Check for numerical instabilities in PRINT file
- Validate mass conservation and energy balance
- Compare gauge measurements for consistency

## References

- SWASH User Manual (included in `docs/swash_manual.md`)
- Experimental protocols in `docs/reports/`
- Configuration templates in `templates/`

## Future Experiments

Planned configurations for future research:
- Irregular wave spectra (`spectrum001.yml`)
- Multiple breakwater configurations (`array001.yml`)
- Climate change scenarios (`future001.yml`)
- Optimization studies (`optimal001.yml`)