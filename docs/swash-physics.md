# SWASH Physics and Modeling

This document explains the physical processes and numerical methods used in SWASH simulations, providing the scientific foundation for understanding parameter choices and interpreting results.

## SWASH Overview

SWASH (Simulating WAves till SHore) is a non-hydrostatic wave-flow model designed for coastal applications. It solves the non-linear shallow water equations with non-hydrostatic pressure correction, enabling accurate modeling of:

- Wave propagation and transformation
- Wave breaking and dissipation
- Flow through porous structures
- Wave-structure interaction
- Overtopping and runup

## Mathematical Foundation

### Governing Equations

SWASH solves the Reynolds-averaged Navier-Stokes equations:

**Continuity Equation:**
$$\frac{\partial u}{\partial x} + \frac{\partial w}{\partial z} = 0$$

**Momentum Equations:**
$$\frac{\partial u}{\partial t} + u\frac{\partial u}{\partial x} + w\frac{\partial u}{\partial z} = -\frac{1}{\rho} \frac{\partial p}{\partial x} + \nu\nabla^2 u + F_x$$

$$\frac{\partial w}{\partial t} + u\frac{\partial w}{\partial x} + w\frac{\partial w}{\partial z} = -\frac{1}{\rho} \frac{\partial p}{\partial z} - g + \nu\nabla^2 w + F_z$$

Where:
- `u`, `w`: horizontal and vertical velocities
- `p`: pressure
- `ρ`: water density
- `ν`: kinematic viscosity
- `Fx`, `Fz`: external forces (vegetation, porous media)

### Non-Hydrostatic Pressure

The key innovation is the non-hydrostatic pressure correction:
$$p = p_{\text{hydrostatic}} + q$$

Where `q` is the non-hydrostatic pressure that captures:
- Wave dispersion effects
- Vertical accelerations
- Short wave phenomena

## Wave Physics

### Wave Propagation

SWASH accurately models wave propagation from deep to shallow water, including:

1. **Shoaling**: Wave height changes due to depth variation
2. **Refraction**: Wave direction changes due to depth gradients
3. **Dispersion**: Frequency-dependent wave speed
4. **Nonlinear Effects**: Wave steepening and harmonics

### Wave Breaking

The framework uses energy-based breaking criteria:

**Breaking Parameters:**
- `BREAKING 0.6 0.3` → $\gamma=0.6$ (breaking parameter), $\alpha=0.3$ (dissipation parameter)
- Breaking occurs when $H/h > \gamma$ (wave height to depth ratio)
- Energy dissipation: $D = \alpha \times \rho \times g \times f_p \times H^2$

**Breaking Types:**
- **Spilling**: Gradual energy dissipation (shallow slopes)
- **Plunging**: Rapid energy loss (steep slopes)
- **Surging**: Minimal breaking (very steep slopes)

### Bottom Friction

Manning friction law:
```
FRICTION MANNING 0.019
```

Friction force: $\tau_b = \rho \times g \times n^2 \times u|u| / h^{4/3}$

Where:
- `n = 0.019`: Manning coefficient (typical for sand/gravel)
- `h`: water depth
- `u`: depth-averaged velocity

## Porous Media Modeling

### Breakwater Representation

Breakwaters are modeled as porous media using:

1. **Volume-averaged equations** within porous regions
2. **Drag forces** representing flow resistance
3. **Inertia coefficients** for unsteady flow effects

### Porosity Implementation

```
POROSITY dn50 height A B T
```

Parameters:
- `dn50`: Median grain diameter (stone size)
- `height`: Structure height
- `A = 200.0`: Drag coefficient
- `B = 1.1`: Inertia coefficient  
- `T`: Wave period (affects Reynolds number)

### Darcy-Forchheimer Equation

Flow through porous media follows:
$$\nabla p = -\frac{\mu}{K} \times u - \frac{\rho \times C_f}{\sqrt{K}} \times u|u|$$

Where:
- `K`: Permeability (function of porosity and grain size)
- `Cf`: Forchheimer coefficient
- First term: viscous losses (Darcy)
- Second term: inertial losses (Forchheimer)

## Vegetation Modeling

### Drag Force Approach

Vegetation resistance is modeled as drag forces:

```
VEGETATION height diameter density drag_coefficient
```

**Force Calculation:**
$$F = 0.5 \times \rho \times C_d \times D \times h \times n \times u|u|$$

Where:
- `Cd`: Drag coefficient
- `D`: Stem diameter
- `h`: Plant height
- `n`: Stem density (stems/m²)
- `u`: Local velocity

### Flow Modification

Vegetation affects flow through:

1. **Momentum absorption**: Direct drag on fluid
2. **Turbulence generation**: Enhanced mixing
3. **Flow deflection**: Vertical velocity components
4. **Wave damping**: Energy dissipation

### Vegetation Types

The framework supports mixed vegetation through:

- **Primary type**: Main vegetation characteristics
- **Secondary type**: Alternative vegetation (optional)
- **Spatial distribution**: Half-domain or alternating patterns

## Boundary Conditions

### Wave Generation (West Boundary)

```
BOUNDCOND SIDE WEST BTYPE WEAKREFL CON REGULAR H T 0.0
```

**Regular Waves:**
- Wave height: `H`
- Wave period: `T`
- Wave direction: 0.0° (shore-normal)
- Weakly reflective boundary reduces spurious reflections

### Wave Absorption (East Boundary)

```
SPONGE EAST 10.0
```

**Sponge Layer:**
- Length: 10.0 m
- Gradually absorbs outgoing waves
- Prevents artificial reflections from domain boundary

## Grid and Discretization

### Computational Grid

```
CGRID REGULAR 0.0 0.0 0.0 112.0 0.0 500 0
VERTICAL 2
```

**Grid Properties:**
- Domain: 112 m × 2 layers
- Resolution: $\Delta x = 0.224$ m
- Vertical layers: 2 (surface and bottom)

**Resolution Criteria:**
- $\Delta x < L/20$ for wave length $L$ (ensures 20 points per wavelength)
- $\Delta t < \Delta x/\sqrt{gh}$ for numerical stability (CFL condition)

### Time Stepping

```
COMPUTE 000000.000 0.05 SEC duration
```

**Adaptive Time Stepping:**
- Initial: $\Delta t = 0.05$ s
- Automatically adjusted for stability
- CFL number < 1 maintained

## Numerical Methods

### Spatial Discretization

- **Finite differences** on structured grid
- **Staggered arrangement**: velocities at cell faces, pressure at centers
- **Higher-order schemes** for accuracy

### Pressure Correction

1. **Hydrostatic step**: Solve without non-hydrostatic pressure
2. **Pressure correction**: Solve Poisson equation for non-hydrostatic pressure
3. **Velocity correction**: Update velocities with pressure gradient

### Convergence Criteria

Iterations continue until:
- Velocity residuals < tolerance
- Mass conservation satisfied
- Pressure field converged

## Physical Processes Summary

### Wave Transformation

| Process | Implementation | Parameters |
|---------|----------------|------------|
| Shoaling | Grid resolution + dispersion | Grid size, depth |
| Breaking | Energy dissipation | $\gamma=0.6$, $\alpha=0.3$ |
| Friction | Manning formula | $n=0.019$ |
| Dispersion | Non-hydrostatic pressure | Automatic |

### Structure Interaction

| Component | Model | Key Parameters |
|-----------|-------|----------------|
| Breakwater | Porous media | Porosity, grain size |
| Vegetation | Drag forces | Height, density, $C_d$ |
| Overtopping | Free surface tracking | Crest geometry |
| Transmission | Momentum balance | Structure porosity |

## Validation and Limitations

### Validated Applications

- Laboratory wave flumes
- Coastal breakwaters
- Vegetated coastlines
- Overtopping studies

### Model Limitations

1. **2D Effects**: Framework uses 1D mode (cross-shore only)
2. **Wave Directional Spreading**: Regular waves only
3. **Sediment Transport**: Not included
4. **Air Entrainment**: Not modeled in overtopping
5. **Structure Flexibility**: Rigid structures assumed

### Numerical Limitations

- **Grid Resolution**: Must resolve shortest waves
- **Time Step**: Limited by CFL condition
- **Domain Size**: Balance between accuracy and computational cost
- **Boundary Effects**: Sponge layers must be adequate

## Best Practices

### Parameter Selection

1. **Wave Conditions**: Ensure realistic wave steepness ($H/L < 0.1$)
2. **Structure Geometry**: Realistic slope angles (1:1 to 3:1)
3. **Porosity Values**: Based on material properties (0.3-0.5 typical)
4. **Grid Resolution**: 15-25 points per wave length minimum

### Validation Approach

1. **Convergence Testing**: Verify grid and time step independence
2. **Mass Conservation**: Check volume balance
3. **Energy Balance**: Verify energy dissipation mechanisms
4. **Physical Reality**: Compare with analytical solutions where possible

## References

- Zijlema, M., Stelling, G., & Smit, P. (2011). SWASH: An operational public domain code for simulating wave fields and rapidly varied flows in coastal waters. *Coastal Engineering*, 58(10), 992-1012.
- SWASH User Manual v11.01A - Complete theoretical background
- Van der Meer, J.W. (2002). Wave run-up and wave overtopping at dikes. Technical Advisory Committee on Flood Defence.

## Next Steps

- [Template Mapping](template-mapping.md) - How physics maps to input files
- [Output Interpretation](output-interpretation.md) - Understanding simulation results
- [Troubleshooting Guide](troubleshooting-guide.md) - Common issues and solutions