# Physics and Parameters Reference

## Overview

This document explains the physical principles and parameter meanings behind the SWASH breakwater modeling framework. Understanding these concepts is essential for proper model setup, result interpretation, and physical insight into coastal engineering problems.

## Wave Theory Fundamentals

### Linear Wave Theory

The framework uses **linear wave theory** as the foundation for wave generation and analysis:

#### Dispersion Relation
```
ω² = gk tanh(kh)
```
Where:
- ω = 2π/T (angular frequency)
- k = 2π/L (wave number)  
- g = 9.81 m/s² (gravitational acceleration)
- h = water depth
- T = wave period
- L = wavelength

#### Wave Classification by Relative Depth

| Condition | Range | Characteristics |
|-----------|-------|------------------|
| **Deep water** | h/L > 0.5 | ω² = gk, L = gT²/(2π) |
| **Intermediate** | 0.05 < h/L < 0.5 | Full dispersion relation |
| **Shallow water** | h/L < 0.05 | ω² = gk²h, L = T√(gh) |

For typical framework conditions (h ≈ 1-4 m, T = 3-12 s):
- **Short periods** (T < 6 s): Intermediate water
- **Long periods** (T > 8 s): Transitioning to shallow water

### Non-hydrostatic Effects

SWASH solves the **non-hydrostatic shallow water equations**, capturing:

#### Vertical Acceleration
```
∂w/∂t + u∂w/∂x + w∂w/∂z = -1/ρ ∂q/∂z - g
```
Where q is the non-hydrostatic pressure accounting for:
- **Frequency dispersion**: Correct wave speeds
- **Short wave effects**: Steep wave propagation
- **Vertical flow structure**: Important for overtopping

#### Hydrostatic vs. Non-hydrostatic

**Hydrostatic assumption**: p = ρg(η - z)
- Valid for long waves (L >> h)
- Breaks down for shorter waves
- Overestimates wave speed in intermediate water

**Non-hydrostatic correction**: p = ρg(η - z) + q(x,z,t)
- Accurate for all wavelengths
- Essential for coastal wave modeling
- Required for breakwater applications

## Breakwater Physics

### Porous Media Flow

The breakwater is modeled as a **porous medium** with flow governed by:

#### Extended Darcy-Forchheimer Equation
```
∂u/∂t + Cu + Du|u| = -1/ρ ∂p/∂x + gSₓ
```

Where:
- **C**: Linear resistance coefficient
- **D**: Nonlinear (Forchheimer) coefficient  
- **u**: Darcy velocity (volume flux)
- **Sₓ**: Body force term

#### Resistance Coefficients

**Linear resistance (C)**:
```
C = (1-n)²gn₍ₘ₎²/(n³K)
```

**Nonlinear resistance (D)**:
```
D = 1.1/(nDₙ₅₀)
```

Where:
- **n**: Porosity (void fraction)
- **Dₙ₅₀**: Median stone diameter
- **K**: Intrinsic permeability
- **nₘ**: Manning coefficient

#### Physical Interpretation

**Linear term (Cu)**:
- Dominates at **low velocities**
- Represents **viscous drag** through pore spaces
- Proportional to stone surface area

**Nonlinear term (Du|u|)**:
- Dominates at **high velocities** (typical in waves)
- Represents **form drag** around stones
- Proportional to stone frontal area

### Porosity Effects

#### Parameter: `breakwater.porosity` (default: 0.4)

**Physical meaning**:
- **Void fraction**: Volume of voids / Total volume
- **Typical values**: 0.3-0.5 for rock structures
- **Affects**: Wave transmission, flow resistance, structural stability

**Impact on wave behavior**:
```yaml
porosity: 0.2    # Dense structure, low transmission
porosity: 0.4    # Typical rubble mound
porosity: 0.6    # Very porous, high transmission (unstable)
```

**Wave transmission scaling**:
- Higher porosity → Higher transmission coefficient
- Lower porosity → More reflection, less transmission

### Stone Size Effects

#### Parameter: `breakwater.armour_dn50` (default: 1.15 m)

**Dₙ₅₀ definition**: Diameter where 50% of stones (by weight) are smaller

**Physical significance**:
- **Flow resistance**: Larger stones → Lower resistance per unit volume
- **Stability**: Larger stones → More stable under wave attack
- **Permeability**: Larger stones → Higher permeability

**Scaling relationships**:
```
D ∝ 1/Dₙ₅₀     (Forchheimer resistance)
K ∝ Dₙ₅₀²      (Permeability)
```

### Breakwater Geometry

#### Slope Effects: `breakwater.slope` (default: 1.75 H:V)

**Wave interaction**:
- **Gentle slopes** (1:3): More breaking, energy dissipation
- **Steep slopes** (1:1.5): More reflection, less breaking
- **Framework default** (1:1.75): Balanced performance

**Stability considerations**:
- Steeper slopes require larger stones
- Gentler slopes are more stable but require more material

#### Crest Width: `breakwater.crest_width` (default: 3.0 m)

**Physical effects**:
- **Wider crest**: More energy dissipation, less overtopping
- **Narrower crest**: Less material, more transmission
- **Settlement protection**: Wider crest accommodates settlement

## Vegetation Physics

### Drag Force Modeling

Vegetation is modeled using **Morison-type drag forces**:

#### Drag Force per Unit Volume
```
Fₓ = ½ρCDaU|U|
```

Where:
- **CD**: Drag coefficient
- **a**: Frontal area per unit volume = N × D × h
- **N**: Plant density (stems/m²)
- **D**: Stem diameter
- **h**: Plant height
- **U**: Flow velocity

#### Implementation in SWASH

**Spatial vegetation using NPLANTS grid**:
- **INPGRID NPLANTS**: Defines spatial density distribution
- **READINP NPLANTS**: Reads `vegetation_density.dat` file
- **Multiplication**: Final density = base density × spatial field

**VEGETATION command parameters**:
1. **Plant height** (m): Vertical extent of drag force
2. **Stem diameter** (m): Individual stem size
3. **Base density** (1.0): Multiplied by spatial NPLANTS field
4. **Drag coefficient**: Shape-dependent resistance factor

### Vegetation Parameters

#### Plant Height: `vegetation.plant_height` (default: 0.5 m)

**Physical considerations**:
- **Effective height**: Portion interacting with flow
- **Submergence ratio**: height/water_depth affects drag
- **Seasonal variation**: Different heights for summer/winter

#### Stem Diameter: `vegetation.plant_diameter` (default: 0.01 m)

**Typical values**:
- **Small vegetation** (grass): 0.002-0.005 m
- **Shrubs** (Rosa rugosa): 0.005-0.015 m
- **Small trees** (Alnus): 0.01-0.03 m

#### Plant Density: `vegetation.plant_density` (default: 10 stems/m²)

**Physical interpretation**:
- **Sparse vegetation**: 1-5 stems/m²
- **Moderate density**: 10-20 stems/m²
- **Dense vegetation**: 20-50 stems/m²
- **Very dense**: >50 stems/m² (may cause numerical issues)

**Spatial application**:
- **Crest-only placement**: Applied only on flat crest portion of breakwater
- **Zero elsewhere**: No vegetation on slopes or in water
- **Automatic calculation**: Crest zone = breakwater extent - 2 × (height × slope)

#### Drag Coefficient: `vegetation.drag_coefficient` (default: 1.0)

**Typical values by vegetation type**:
- **Rigid cylinders**: CD ≈ 1.0-1.2
- **Flexible vegetation**: CD ≈ 0.5-1.5 (depends on bending)
- **With foliage**: CD ≈ 1.5-3.0 (seasonal variation)

### Reynolds Number Effects

#### Flow Regime Classification
```
Re = UD/ν
```

Where:
- **U**: Flow velocity
- **D**: Stem diameter  
- **ν**: Kinematic viscosity ≈ 1×10⁻⁶ m²/s

**Drag coefficient variation**:
- **Re < 200**: CD decreases with Re (viscous regime)
- **200 < Re < 10⁵**: CD ≈ 1.0-1.2 (constant, typical for waves)
- **Re > 10⁵**: CD decreases (turbulent boundary layer)

## Wave Generation and Absorption

### Incident Wave Conditions

#### Regular Waves: `water.wave_height`, `water.wave_period`

**Advantages of regular waves**:
- **Systematic analysis**: Clear cause-effect relationships
- **Parameter studies**: Easier to isolate effects
- **Theoretical comparison**: Linear theory predictions available

**Wave steepness limits**:
```
H/L < 0.142    (Breaking limit)
H/L < 0.1      (Typical design limit)
```

#### Wave Generation Method

**Weakly reflective boundary** (`BTYPE WEAKREFL`):
- Absorbs **reflected waves** from structure
- Prevents **spurious reflections** that contaminate incident conditions
- Maintains **steady incident conditions**

### Boundary Conditions

#### Wave Absorption: Sponge Layer

**Purpose**: Absorb transmitted waves to prevent end-wall reflection

**Implementation**: 
```swash
SPONGE EAST 10.0
```

**Sponge length choice**:
- **Too short**: Incomplete absorption, spurious reflection
- **Too long**: Reduces useful domain, computational waste
- **Framework default** (10 m): ≈ 1 wavelength for typical conditions

#### Lateral Boundaries

**1D simulation**: No lateral boundaries (infinite width assumption)
- **Appropriate for**: Channel experiments, 2D structure cross-sections
- **Limitation**: Cannot model 3D effects, diffraction around structure ends

## Numerical Modeling

### Temporal Discretization

#### Adaptive Time Stepping

**CFL condition**: `Δt ≤ CFL × Δx/√(gh)`

**Framework settings**:
```swash
TIMEINT METH EXPLICIT 0.4 0.8
```

**CFL range explanation**:
- **Lower bound** (0.4): Ensures numerical accuracy
- **Upper bound** (0.8): Maintains stability
- **Adaptive**: SWASH adjusts based on local conditions

#### Time Step Control: `numeric.time_step` (default: 0.05 s)

**Role**: Initial time step for adaptive algorithm
- SWASH **adjusts automatically** based on stability
- Smaller initial value → More conservative start
- Larger initial value → Faster startup (if stable)

### Spatial Discretization

#### Grid Resolution: `grid.nx_cells` (default: 500)

**Resolution requirements**:
```
Δx ≤ L/20    (Minimum for wave propagation)
Δx ≤ L/50    (Good accuracy)
Δx ≤ L/100   (High accuracy)
```

**For framework defaults**:
- Domain length: 112 m
- Grid cells: 500
- Resolution: Δx = 0.224 m
- Shortest wavelength (T=3s, h=1m): L ≈ 13 m
- Resolution ratio: L/Δx ≈ 58 (adequate)

#### Vertical Layers: `grid.n_layers` (default: 2)

**Layer distribution**:
- **Equidistant**: Equal thickness layers
- **More layers**: Better vertical velocity structure
- **Computational cost**: Scales approximately linearly

**Layer guidelines**:
- **1 layer**: Depth-averaged (hydrostatic)
- **2 layers**: Minimum for non-hydrostatic
- **3-4 layers**: Good accuracy for most applications
- **>5 layers**: Diminishing returns for additional cost

### Non-hydrostatic Solver

#### Box Scheme: `NONHYDROSTATIC BOX 1.0`

**Box scheme characteristics**:
- **Implicit**: Unconditionally stable
- **θ = 1.0**: Fully implicit (most stable)
- **θ = 0.5**: Crank-Nicolson (more accurate but less stable)

**Alternative options**:
- **θ = 0.0**: Explicit (unstable for non-hydrostatic)
- **Framework choice**: θ = 1.0 for robustness

## Physical Processes

### Wave Breaking

#### Breaking Criteria: `BREAKING 0.6 0.3`

**Applied when**: `grid.n_layers ≤ 3`

**Parameters**:
1. **Breaking index** (0.6): γ = H/h threshold for breaking
2. **Maximum gamma** (0.3): Limits energy dissipation rate

**Physical meaning**:
- **Breaking index**: Lower values → Earlier breaking
- **Energy dissipation**: Prevents unrealistic wave heights
- **Coarse grid compensation**: Extra dissipation for low vertical resolution

### Bottom Friction

#### Manning Friction: `FRICTION MANNING 0.019`

**Manning coefficient choice**:
- **Smooth concrete**: n = 0.012-0.014
- **Rock/stone**: n = 0.015-0.025  
- **Framework value**: n = 0.019 (intermediate, rock-like)

**Physical effects**:
- **Energy dissipation**: Reduces wave heights through propagation
- **Velocity profiles**: Affects near-bottom velocities
- **Overtopping**: Influences flow over breakwater crest

### Water Properties

#### Density Effects: `water.water_density` (default: 1000 kg/m³)

**Typical values**:
- **Freshwater**: 1000 kg/m³
- **Seawater**: 1025 kg/m³
- **Cold water**: Up to 1030 kg/m³

**Impact on physics**:
- **Buoyancy**: Affects relative density Δ = (ρₛ - ρw)/ρw
- **Hydrostatic pressure**: ρg(η - z)
- **Stone stability**: Higher density → Higher stability

## Dimensional Analysis and Scaling

### Similarity Parameters

#### Froude Number
```
Fr = U/√(gL)
```

**Physical meaning**: Ratio of inertial to gravitational forces
- **Fr < 1**: Subcritical flow (typical for waves)
- **Fr = 1**: Critical flow (hydraulic control)
- **Fr > 1**: Supercritical flow (rare in coastal engineering)

#### Wave Steepness
```
S = H/L
```

**Applications**:
- **Wave breaking**: S > 0.142 → Breaking
- **Linear theory validity**: S < 0.1 → Linear theory applicable
- **Nonlinear effects**: S > 0.05 → Nonlinear effects important

#### Relative Depth
```
kh = 2πh/L
```

**Wave regime classification**:
- **kh < 0.3**: Shallow water (L >> h)
- **0.3 < kh < 3**: Intermediate water (L ~ h)
- **kh > 3**: Deep water (L << h)

### Scaling Laws

#### Geometric Scaling (Froude Scaling)

**Scale factor**: λL (length scale)

**Derived scales**:
- **Time**: λT = √λL
- **Velocity**: λU = √λL  
- **Force**: λF = λL³
- **Pressure**: λp = λL

**Framework applications**:
- **Laboratory scale**: 1:50 typical
- **Physical model scaling**: Maintain Froude similarity
- **Prototype extrapolation**: Scale results to field conditions

## Parameter Sensitivity and Optimization

### Critical Parameters

#### High Sensitivity Parameters
1. **Wave height**: Quadratic effect on forces and overtopping
2. **Wave period**: Affects wavelength, steepness, and resonance
3. **Water level**: Controls freeboard and breaking location
4. **Breakwater porosity**: Strong influence on transmission

#### Moderate Sensitivity Parameters
1. **Crest width**: Linear effect on overtopping reduction
2. **Stone size**: Affects resistance coefficients
3. **Vegetation density**: Proportional effect on drag force

#### Low Sensitivity Parameters
1. **Grid resolution**: Affects accuracy, not physics (within reasonable range)
2. **Time step**: Numerical parameter (adaptive)
3. **Friction coefficient**: Small effect for short propagation distances

### Design Guidelines

#### Wave Conditions
```yaml
# Conservative design
water:
  wave_height: 2.4    # 100-year storm
  wave_period: 8.0    # Energetic period
  water_level: 3.6    # High water + sea level rise

# Typical conditions
water:
  wave_height: 1.0    # Annual storm
  wave_period: 6.0    # Average period
  water_level: 1.6    # Mean high water
```

#### Structure Optimization
```yaml
# High protection (low transmission)
breakwater:
  crest_height: 3.0   # High freeboard
  crest_width: 5.0    # Wide crest
  porosity: 0.3       # Dense structure

# Cost-optimized (moderate protection)
breakwater:
  crest_height: 2.0   # Moderate freeboard
  crest_width: 3.0    # Standard width
  porosity: 0.4       # Typical porosity
```

#### Vegetation Enhancement
```yaml
# Maximum vegetation benefit
vegetation:
  enable: true
  plant_height: 0.8   # Tall vegetation
  plant_density: 20   # Dense coverage
  drag_coefficient: 2.0  # High drag (with foliage)

# Moderate vegetation
vegetation:
  enable: true
  plant_height: 0.5   # Medium height
  plant_density: 10   # Moderate density
  drag_coefficient: 1.0  # Standard drag
```

## Physical Limitations and Assumptions

### Model Limitations

#### Geometric Assumptions
- **1D simulation**: No lateral effects or diffraction
- **Regular geometry**: Uniform cross-section
- **Rigid structure**: No deformation or settlement

#### Physical Assumptions  
- **Regular waves**: No irregular wave spectrum effects
- **Isothermal**: No thermal stratification
- **Incompressible**: No acoustic effects
- **Clear water**: No sediment transport

#### Vegetation Limitations
- **Rigid vegetation**: No bending or flexibility
- **Uniform distribution**: No spatial heterogeneity
- **No growth/decay**: Static vegetation properties
- **No root effects**: Only above-ground vegetation

### Validity Ranges

#### Wave Conditions
```
0.1 m < H < 5.0 m      (Wave height)
3 s < T < 15 s         (Wave period)  
0.5 m < h < 10 m       (Water depth)
H/L < 0.1              (Wave steepness)
```

#### Structure Geometry
```
1 m < crest_height < 5 m     (Structure height)
1 m < crest_width < 10 m     (Crest width)
1.5 < slope < 3.0            (Side slopes H:V)
0.2 < porosity < 0.6         (Void fraction)
```

#### Vegetation Parameters
```
0.1 m < plant_height < 2 m   (Plant height)
0.001 m < diameter < 0.05 m  (Stem diameter)
1 < density < 100 stems/m²   (Plant density)
0.5 < CD < 3.0               (Drag coefficient)
```

## Next Steps

- **[Configuration Guide](configuration-guide.md)**: Apply physical understanding to parameter selection
- **[Input File Reference](input-file-reference.md)**: See how physics translates to SWASH commands
- **[Output Reference](output-reference.md)**: Interpret results using physical principles
- **[Troubleshooting](troubleshooting.md)**: Debug issues using physical reasoning