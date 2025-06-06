# SWASH Output Reference

## Overview

This document describes the output files generated by SWASH simulations and provides guidance for interpreting results. The framework produces both time series data at specific gauge locations and spatial field data across the computational domain.

## Output File Structure

After a successful simulation, the output directory contains:

```
simulations/{name}_{hash}/
├── INPUT                    # Generated SWASH input file
├── PRINT                    # SWASH execution log
├── bathymetry.dat          # Input: Bottom elevations
├── porosity.dat            # Input: Porosity field
├── structure_height.dat    # Input: Structure height
├── vegetation_density.dat  # Input: Vegetation density (if enabled)
├── wg01.dat               # Output: Wave gauge 1 time series
├── wg02.dat               # Output: Wave gauge 2 time series
├── wg03.dat               # Output: Wave gauge 3 time series
├── wg04.dat               # Output: Wave gauge 4 time series
├── wg05.dat               # Output: Wave gauge 5 time series
├── final_state.mat        # Output: Spatial fields at final time
├── norm_end               # Output: Convergence information
└── swashinit              # SWASH initialization data
```

## Time Series Output Files

### Wave Gauge Data (`wg*.dat`)

#### File Format
Each wave gauge file contains time series data in **ASCII format** with **scientific notation**:

```
 0.00000000E+00  1.00000000E+00  0.00000000E+00 
 1.00000000E-01  1.02342156E+00  3.45123456E-02 
 2.00000000E-01  1.04521234E+00  4.12345678E-02 
 ...
```

#### Column Structure
| Column | Variable | Units | Description |
|--------|----------|-------|-------------|
| 1 | Time | s | Simulation time from start |
| 2 | Water Level | m | Free surface elevation η(t) |
| 3 | U-velocity | m/s | Horizontal velocity u(t) |

**Note**: The framework uses 1D simulation, so V-velocity is always zero and not included.

#### Gauge Locations
Default gauge positions (configurable via `numeric.wave_gauge_positions`):

| Gauge | Position | Purpose |
|-------|----------|---------|
| WG01 | 20.0 m | Incident wave conditions |
| WG02 | 60.0 m | Pre-structure baseline |
| WG03 | 65.0 m | Near-structure approach |
| WG04 | 80.0 m | Close to structure |
| WG05 | 100.0 m | At structure location |

#### Data Characteristics

**Temporal Resolution**:
- **Frequency**: Controlled by `numeric.output_interval` (default: 0.1 s)
- **Duration**: `numeric.n_waves × water.wave_period` (default: 50 × 6.0 = 300 s)
- **Total points**: Duration / output_interval (default: 3000 points)

**Physical Variables**:
- **Water level**: Instantaneous free surface elevation above still water level
- **Velocity**: Depth-averaged horizontal velocity (for 1D)
- **Sign convention**: Positive velocity in +x direction (wave propagation direction)

### Data Loading Examples

#### Python (NumPy)
```python
import numpy as np

# Load wave gauge data
data = np.loadtxt('simulations/dev_12345678/wg01.dat')
time = data[:, 0]           # Time [s]
eta = data[:, 1]            # Water level [m]
u = data[:, 2]              # Velocity [m/s]

# Basic analysis
mean_level = np.mean(eta)   # Mean water level (setup)
max_eta = np.max(eta)       # Maximum elevation
min_eta = np.min(eta)       # Minimum elevation
wave_height = max_eta - min_eta  # Approximate wave height
```

#### Python (Pandas)
```python
import pandas as pd

# Load with column names
columns = ['time', 'eta', 'u']
df = pd.read_csv('simulations/dev_12345678/wg01.dat', 
                 sep=r'\s+', header=None, names=columns)

# Time series analysis
df['eta_detrended'] = df['eta'] - df['eta'].mean()
wave_heights = []  # Implement zero-crossing analysis
```

#### MATLAB
```matlab
% Load wave gauge data
data = load('simulations/dev_12345678/wg01.dat');
time = data(:, 1);
eta = data(:, 2);
u = data(:, 3);

% Wave analysis
[Hs, Tp, setup] = wave_analysis(time, eta);
```

## Spatial Output Files

### Final State Data (`final_state.mat`)

#### File Format
**MATLAB binary format** containing spatial field data at the final time step.

#### Variables Included
| Variable | Description | Units |
|----------|-------------|-------|
| `WATLEV` | Water level field | m |
| `VEL` | Velocity field | m/s |
| `HSIG` | Significant wave height | m |
| `SETUP` | Mean water level setup | m |

#### Spatial Resolution
- **Grid spacing**: Every 4th computational cell (configurable)
- **Default resolution**: 112 m / (500/4) = 0.896 m
- **Total points**: `grid.nx_cells // 4` + 1

#### Data Loading

**MATLAB**:
```matlab
% Load spatial data
data = load('simulations/dev_12345678/final_state.mat');

% Extract fields
x = linspace(0, 112, length(data.WATLEV));
watlev = data.WATLEV;
vel = data.VEL;
hsig = data.HSIG;
setup = data.SETUP;

% Plot results
figure;
subplot(2,2,1); plot(x, watlev); title('Water Level');
subplot(2,2,2); plot(x, vel); title('Velocity');
subplot(2,2,3); plot(x, hsig); title('Significant Wave Height');
subplot(2,2,4); plot(x, setup); title('Wave Setup');
```

**Python (scipy)**:
```python
from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt

# Load MATLAB file
data = loadmat('simulations/dev_12345678/final_state.mat')

# Extract fields (MATLAB arrays are squeezed)
watlev = data['WATLEV'].squeeze()
vel = data['VEL'].squeeze()
hsig = data['HSIG'].squeeze()
setup = data['SETUP'].squeeze()

# Create spatial coordinate
x = np.linspace(0, 112, len(watlev))

# Plot results
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
ax1.plot(x, watlev); ax1.set_title('Water Level')
ax2.plot(x, vel); ax2.set_title('Velocity')
ax3.plot(x, hsig); ax3.set_title('Significant Wave Height')
ax4.plot(x, setup); ax4.set_title('Wave Setup')
plt.tight_layout()
```

## Log and Diagnostic Files

### PRINT File

#### Content Overview
The PRINT file contains the complete SWASH execution log with:

1. **Header information**: SWASH version, execution time
2. **Input echo**: All commands from INPUT file
3. **Initialization**: Grid setup, boundary conditions
4. **Time stepping**: Progress indicators and timestamps
5. **Convergence**: Numerical solver information
6. **Completion**: Final status and timing

#### Key Information Sections

**Execution Progress**:
```
Time of simulation  ->  000259.975         in sec:        179.97500
Time of simulation  ->  000300.000         in sec:        180.00000
```
- Shows simulation time (HHMMSS format) and equivalent seconds
- Useful for monitoring long simulations

**Error Messages** (if any):
```
** Error            : Description of error
** Severe error     : Critical error description
** Warning          : Non-fatal warning
```

**Completion Status**:
```
STOP
```
- Indicates normal completion
- Absence suggests abnormal termination

#### Monitoring Simulation Progress

**Real-time monitoring**:
```bash
# Watch simulation progress
tail -f simulations/dev_12345678/PRINT

# Check if simulation is still running
ps aux | grep swash

# Monitor output file growth
watch ls -lh simulations/dev_12345678/
```

### Convergence Information (`norm_end`)

#### Purpose
Contains numerical solver convergence information for diagnosing solution quality.

#### Typical Content
```
Final residual norms and convergence information
Pressure solver iterations and residuals
```

**Interpretation**:
- **Small residuals**: Good convergence
- **Large residuals**: Potential numerical issues
- **Non-decreasing residuals**: Convergence problems

### Initialization File (`swashinit`)

#### Purpose
Internal SWASH file containing grid and initialization data.

**Usage**: Primarily for SWASH internal use and debugging.

## Data Analysis and Interpretation

### Wave Analysis Techniques

#### Zero-Crossing Analysis
```python
def zero_crossing_analysis(time, eta):
    """Analyze waves using zero-crossing method."""
    # Remove mean (setup)
    eta_detrended = eta - np.mean(eta)
    
    # Find zero crossings
    zero_crossings = np.where(np.diff(np.sign(eta_detrended)))[0]
    
    # Extract individual waves
    wave_heights = []
    wave_periods = []
    
    for i in range(0, len(zero_crossings)-2, 2):
        # Wave height: trough to crest
        wave_segment = eta_detrended[zero_crossings[i]:zero_crossings[i+2]]
        H = np.max(wave_segment) - np.min(wave_segment)
        wave_heights.append(H)
        
        # Wave period: zero to zero
        T = time[zero_crossings[i+2]] - time[zero_crossings[i]]
        wave_periods.append(T)
    
    return np.array(wave_heights), np.array(wave_periods)

# Statistical analysis
def wave_statistics(wave_heights):
    """Calculate wave height statistics."""
    Hs = np.mean(np.sort(wave_heights)[-len(wave_heights)//3:])  # Significant height
    Hmax = np.max(wave_heights)                                   # Maximum height
    Hmean = np.mean(wave_heights)                                 # Mean height
    return Hs, Hmax, Hmean
```

#### Spectral Analysis
```python
from scipy import signal

def spectral_analysis(time, eta, window='hann'):
    """Compute wave energy spectrum."""
    # Remove mean
    eta_detrended = eta - np.mean(eta)
    
    # Compute power spectral density
    dt = time[1] - time[0]
    frequencies, psd = signal.welch(eta_detrended, 1/dt, window=window)
    
    # Convert to wave energy spectrum
    energy_spectrum = psd * 2  # One-sided spectrum
    
    return frequencies, energy_spectrum

# Peak frequency analysis
def peak_frequency(frequencies, spectrum):
    """Find peak frequency and corresponding period."""
    peak_idx = np.argmax(spectrum)
    fp = frequencies[peak_idx]
    Tp = 1 / fp if fp > 0 else np.inf
    return fp, Tp
```

### Transmission Analysis

#### Wave Transmission Coefficient
```python
def transmission_coefficient(eta_incident, eta_transmitted):
    """Calculate wave transmission coefficient."""
    # Use zero-crossing analysis for both gauges
    H_inc, _ = zero_crossing_analysis(time, eta_incident)
    H_trans, _ = zero_crossing_analysis(time, eta_transmitted)
    
    # Statistical measures
    Hs_inc = wave_statistics(H_inc)[0]
    Hs_trans = wave_statistics(H_trans)[0]
    
    # Transmission coefficient
    Kt = Hs_trans / Hs_inc
    
    return Kt

# Example usage
data_inc = np.loadtxt('wg01.dat')   # Incident gauge
data_trans = np.loadtxt('wg05.dat') # Transmitted gauge

Kt = transmission_coefficient(data_inc[:, 1], data_trans[:, 1])
print(f"Transmission coefficient: {Kt:.3f}")
```

#### Wave Setup Analysis
```python
def wave_setup_analysis(time, eta, settling_time=60.0):
    """Analyze wave-induced setup."""
    # Remove initial transient
    steady_idx = time > settling_time
    eta_steady = eta[steady_idx]
    
    # Mean water level (setup)
    setup = np.mean(eta_steady)
    
    # Setup standard deviation (measure of variability)
    setup_std = np.std(eta_steady)
    
    return setup, setup_std

# Compare setup at different locations
setup_values = []
for i in range(1, 6):
    data = np.loadtxt(f'wg0{i}.dat')
    setup, _ = wave_setup_analysis(data[:, 0], data[:, 1])
    setup_values.append(setup)

# Plot setup variation
import matplotlib.pyplot as plt
gauge_positions = [20, 60, 65, 80, 100]
plt.plot(gauge_positions, setup_values, 'o-')
plt.xlabel('Position (m)')
plt.ylabel('Wave Setup (m)')
plt.title('Wave Setup Distribution')
```

### Overtopping Analysis

#### Overtopping Detection
```python
def overtopping_analysis(time, eta, crest_level, output_interval):
    """Analyze wave overtopping events."""
    # Find overtopping events
    overtopping = eta > crest_level
    
    # Overtopping volume per unit width
    overtopping_volume = np.sum(overtopping * (eta - crest_level)) * output_interval
    
    # Overtopping discharge (volume per unit time per unit width)
    total_time = time[-1] - time[0]
    q = overtopping_volume / total_time
    
    # Number of overtopping events
    overtopping_events = np.sum(np.diff(overtopping.astype(int)) == 1)
    
    return q, overtopping_events, overtopping_volume

# Example for breakwater crest
crest_height = 2.0  # From configuration
water_level = 1.0   # From configuration
crest_level = water_level + crest_height

data = np.loadtxt('wg05.dat')  # Gauge at structure
q, events, volume = overtopping_analysis(data[:, 0], data[:, 1], 
                                        crest_level, 0.1)

print(f"Overtopping discharge: {q:.6f} m³/s/m")
print(f"Number of overtopping events: {events}")
print(f"Total overtopping volume: {volume:.3f} m³/m")
```

## Vegetation Effects Analysis

### Drag Force Estimation
```python
def vegetation_drag_analysis(time, u, vegetation_config):
    """Estimate vegetation drag effects."""
    # Vegetation parameters
    height = vegetation_config['plant_height']
    diameter = vegetation_config['plant_diameter']
    density = vegetation_config['plant_density']
    CD = vegetation_config['drag_coefficient']
    
    # Frontal area per unit volume
    a = density * diameter * height  # [m²/m³]
    
    # Drag force per unit volume
    rho = 1000  # Water density
    drag_force = 0.5 * rho * CD * a * u * np.abs(u)
    
    # Power dissipation
    power_dissipation = drag_force * u
    
    return drag_force, power_dissipation

# Compare with and without vegetation
data_veg = np.loadtxt('simulations/veg_on_12345/wg05.dat')
data_no_veg = np.loadtxt('simulations/veg_off_67890/wg05.dat')

# Velocity comparison
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(data_no_veg[:, 0], data_no_veg[:, 2], label='No vegetation')
plt.plot(data_veg[:, 0], data_veg[:, 2], label='With vegetation')
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.legend()
plt.title('Velocity Comparison')

plt.subplot(1, 2, 2)
plt.plot(data_no_veg[:, 0], data_no_veg[:, 1], label='No vegetation')
plt.plot(data_veg[:, 0], data_veg[:, 1], label='With vegetation')
plt.xlabel('Time (s)')
plt.ylabel('Water Level (m)')
plt.legend()
plt.title('Water Level Comparison')
plt.tight_layout()
```

## Quality Control and Validation

### Data Quality Checks

#### Time Series Validation
```python
def quality_control(time, eta, u):
    """Perform basic quality control checks."""
    issues = []
    
    # Check for NaN or infinite values
    if np.any(~np.isfinite(eta)):
        issues.append("Non-finite values in water level")
    if np.any(~np.isfinite(u)):
        issues.append("Non-finite values in velocity")
    
    # Check time series consistency
    dt = np.diff(time)
    if not np.allclose(dt, dt[0], rtol=1e-6):
        issues.append("Non-uniform time spacing")
    
    # Check for extreme values
    if np.max(np.abs(eta)) > 10:
        issues.append("Unrealistic water levels (>10 m)")
    if np.max(np.abs(u)) > 20:
        issues.append("Unrealistic velocities (>20 m/s)")
    
    # Check for energy conservation
    energy = 0.5 * u**2 + 9.81 * eta  # Specific energy
    energy_drift = np.std(energy) / np.mean(energy)
    if energy_drift > 0.1:
        issues.append("Large energy drift (poor conservation)")
    
    return issues

# Run quality control
for i in range(1, 6):
    data = np.loadtxt(f'wg0{i}.dat')
    issues = quality_control(data[:, 0], data[:, 1], data[:, 2])
    if issues:
        print(f"WG{i:02d} issues: {', '.join(issues)}")
    else:
        print(f"WG{i:02d}: OK")
```

#### Spatial Field Validation
```python
def validate_spatial_fields(final_state_file):
    """Validate spatial field data."""
    from scipy.io import loadmat
    
    data = loadmat(final_state_file)
    issues = []
    
    # Check field consistency
    fields = ['WATLEV', 'VEL', 'HSIG', 'SETUP']
    sizes = []
    
    for field in fields:
        if field in data:
            field_data = data[field].squeeze()
            sizes.append(len(field_data))
            
            # Check for non-finite values
            if np.any(~np.isfinite(field_data)):
                issues.append(f"Non-finite values in {field}")
        else:
            issues.append(f"Missing field: {field}")
    
    # Check size consistency
    if len(set(sizes)) > 1:
        issues.append("Inconsistent field sizes")
    
    return issues
```

### Performance Metrics

#### Computational Efficiency
```python
def simulation_performance(print_file):
    """Extract performance metrics from PRINT file."""
    import re
    
    with open(print_file, 'r') as f:
        content = f.read()
    
    # Find execution time information
    time_pattern = r'Time of simulation\s+->\s+(\d{9}\.\d{3})\s+in sec:\s+(\d+\.\d+)'
    time_matches = re.findall(time_pattern, content)
    
    if time_matches:
        # Last time step
        final_sim_time = float(time_matches[-1][1])
        
        # Total simulation steps
        total_steps = len(time_matches)
        
        # Average time step
        avg_dt = final_sim_time / total_steps if total_steps > 0 else 0
        
        return {
            'total_simulation_time': final_sim_time,
            'total_steps': total_steps,
            'average_time_step': avg_dt,
            'steps_per_second': total_steps / final_sim_time if final_sim_time > 0 else 0
        }
    
    return None

# Example usage
perf = simulation_performance('simulations/dev_12345678/PRINT')
if perf:
    print(f"Simulation completed in {perf['total_steps']} steps")
    print(f"Average time step: {perf['average_time_step']:.4f} s")
    print(f"Computational efficiency: {perf['steps_per_second']:.1f} steps/s")
```

## Troubleshooting Output Issues

### Common Problems

#### Missing Output Files
**Problem**: Expected output files not generated
**Causes**:
- Simulation terminated early due to errors
- Insufficient disk space
- Permission issues

**Diagnosis**:
```bash
# Check PRINT file for errors
grep -i error simulations/dev_12345/PRINT

# Check disk space
df -h simulations/

# Verify simulation completed
tail simulations/dev_12345/PRINT | grep STOP
```

#### Corrupted Data Files
**Problem**: Cannot read data files or unrealistic values
**Causes**:
- Simulation terminated during file writing
- Numerical instability
- Hardware issues

**Diagnosis**:
```python
# Check file integrity
try:
    data = np.loadtxt('wg01.dat')
    print(f"File loaded: {data.shape}")
    print(f"Data range: [{np.min(data):.3e}, {np.max(data):.3e}]")
except Exception as e:
    print(f"Error loading file: {e}")
```

#### Unexpected Results
**Problem**: Results don't match physical expectations
**Causes**:
- Incorrect configuration parameters
- Inappropriate boundary conditions
- Numerical resolution issues

**Diagnosis**:
1. **Check configuration**: Review parameter values for physical realism
2. **Grid convergence**: Test with finer grid resolution
3. **Time step analysis**: Check adaptive time stepping behavior
4. **Boundary effects**: Verify sponge layer effectiveness

## Data Export and Visualization

### Export to Standard Formats

#### CSV Export
```python
def export_to_csv(input_file, output_file):
    """Convert SWASH output to CSV format."""
    data = np.loadtxt(input_file)
    
    # Create DataFrame with proper headers
    import pandas as pd
    df = pd.DataFrame(data, columns=['Time_s', 'WaterLevel_m', 'Velocity_ms'])
    
    # Add metadata
    df.attrs['source'] = input_file
    df.attrs['description'] = 'SWASH wave gauge output'
    
    # Export to CSV
    df.to_csv(output_file, index=False)
    
    return df

# Export all gauges
for i in range(1, 6):
    input_file = f'simulations/dev_12345/wg{i:02d}.dat'
    output_file = f'results/gauge_{i:02d}.csv'
    export_to_csv(input_file, output_file)
```

#### NetCDF Export
```python
def export_to_netcdf(simulation_dir, output_file):
    """Export SWASH results to NetCDF format."""
    import xarray as xr
    
    # Load time series data
    time_series = {}
    gauge_positions = [20, 60, 65, 80, 100]  # From configuration
    
    for i, pos in enumerate(gauge_positions, 1):
        data = np.loadtxt(f'{simulation_dir}/wg{i:02d}.dat')
        time_series[f'gauge_{i:02d}'] = {
            'time': data[:, 0],
            'water_level': data[:, 1],
            'velocity': data[:, 2],
            'position': pos
        }
    
    # Create xarray Dataset
    time_coord = time_series['gauge_01']['time']
    
    ds = xr.Dataset({
        'water_level': (['gauge', 'time'], 
                       np.array([ts['water_level'] for ts in time_series.values()])),
        'velocity': (['gauge', 'time'],
                    np.array([ts['velocity'] for ts in time_series.values()]))
    }, coords={
        'gauge': list(range(1, 6)),
        'time': time_coord,
        'position': ('gauge', gauge_positions)
    })
    
    # Add attributes
    ds.attrs['title'] = 'SWASH Breakwater Simulation Results'
    ds.attrs['source'] = 'SWASH wave model'
    ds.water_level.attrs['units'] = 'm'
    ds.water_level.attrs['long_name'] = 'Water surface elevation'
    ds.velocity.attrs['units'] = 'm/s'
    ds.velocity.attrs['long_name'] = 'Horizontal velocity'
    
    # Save to NetCDF
    ds.to_netcdf(output_file)
    
    return ds
```

## Next Steps

- **[Configuration Guide](configuration-guide.md)**: Adjust parameters based on output analysis
- **[Physics and Parameters](physics-and-parameters.md)**: Understand physical meaning of results
- **[Simulation Workflow](simulation-workflow.md)**: Set up systematic result collection
- **[Troubleshooting](troubleshooting.md)**: Solve output-related issues