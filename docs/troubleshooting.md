# Troubleshooting Guide

## Overview

This guide provides solutions for common issues encountered when using the SWASH breakwater modeling framework. Issues are organized by category with step-by-step diagnostic procedures and solutions.

## Quick Diagnostic Checklist

Before diving into specific issues, run this quick checklist:

```bash
# 1. Check SWASH installation
which swash
swash --version  # If available

# 2. Verify framework installation  
swg --help

# 3. Check Python environment
python --version
pip list | grep -E "(pydantic|ruamel|jinja2|numpy)"

# 4. Test basic functionality
swg create config/test.yml
swg run config/test.yml

# 5. Check disk space and permissions
df -h .
ls -la simulations/
```

## Installation and Environment Issues

### SWASH Not Found

#### Symptoms
```bash
FileNotFoundError: [Errno 2] No such file or directory: 'swash'
SWASH executable not found. Please ensure SWASH is installed and in PATH
```

#### Diagnosis
```bash
# Check if SWASH is installed
which swash
whereis swash
find /usr /opt /home -name "swash" 2>/dev/null
```

#### Solutions

**Option 1: Add SWASH to PATH**
```bash
# Find SWASH installation directory
export PATH=$PATH:/path/to/swash/bin

# Make permanent (add to ~/.bashrc or ~/.profile)
echo 'export PATH=$PATH:/path/to/swash/bin' >> ~/.bashrc
source ~/.bashrc
```

**Option 2: Create symbolic link**
```bash
# If SWASH is installed but not in PATH
sudo ln -s /path/to/swash/bin/swash /usr/local/bin/swash
```

**Option 3: Install SWASH**
- Download from [SWASH website](http://swash.sourceforge.net/)
- Follow installation instructions for your operating system
- Verify installation: `swash --help` or `swash -h`

### Python Environment Issues

#### Symptoms
```bash
ModuleNotFoundError: No module named 'pydantic'
ImportError: cannot import name 'Field' from 'pydantic'
```

#### Solutions

**Using pip**:
```bash
# Install required packages
pip install pydantic ruamel.yaml jinja2 numpy typer

# Or install in editable mode
pip install -e .
```

**Using uv (recommended)**:
```bash
# Install with uv
uv sync

# Activate environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

**Virtual environment isolation**:
```bash
# Create clean environment
python -m venv swash_env
source swash_env/bin/activate
pip install -e .
```

## Configuration Issues

### YAML Syntax Errors

#### Symptoms
```bash
yaml.scanner.ScannerError: mapping values are not allowed here
yaml.parser.ParserError: expected <block end>, but found '<scalar>'
```

#### Common YAML Mistakes

**Incorrect indentation**:
```yaml
# Wrong
water:
wave_height: 0.6          # Missing indentation

# Correct  
water:
  wave_height: 0.6        # Proper indentation (2 spaces)
```

**Mixed tabs and spaces**:
```yaml
# Wrong (mixing tabs and spaces)
water:
	wave_height: 0.6      # Tab character
  wave_period: 6.0        # Spaces

# Correct (consistent spaces)
water:
  wave_height: 0.6        # Spaces only
  wave_period: 6.0        # Spaces only
```

**Missing colons**:
```yaml
# Wrong
water
  wave_height: 0.6

# Correct
water:
  wave_height: 0.6
```

#### Validation

**Check YAML syntax**:
```bash
# Python YAML validation
python -c "import yaml; yaml.safe_load(open('config/test.yml'))"

# Online YAML validator
# Copy-paste content to https://yamlvalidator.com/
```

### Parameter Type Errors

#### Symptoms
```bash
ValidationError: 1 validation error for Config
water.wave_height
  Input should be a valid number, got 'medium'
```

#### Common Type Issues

**String instead of number**:
```yaml
# Wrong
wave_height: "0.6"        # String
n_waves: "50"             # String

# Correct
wave_height: 0.6          # Float
n_waves: 50               # Integer
```

**Wrong numeric type**:
```yaml
# Wrong
n_waves: 50.0             # Float instead of int

# Correct
n_waves: 50               # Integer
```

**Boolean formatting**:
```yaml
# Wrong
enable: "true"            # String
enable: 1                 # Integer

# Correct  
enable: true              # Boolean
enable: false             # Boolean
```

#### Parameter Validation

**Check parameter types**:
```python
# Validate configuration programmatically
from src.config import Config
import yaml

with open('config/test.yml') as f:
    data = yaml.safe_load(f)

try:
    config = Config(name='test', **data)
    print("Configuration valid")
except Exception as e:
    print(f"Validation error: {e}")
```

### Missing Required Parameters

#### Symptoms
```bash
ValidationError: Field required
KeyError: 'wave_height'
```

#### Solutions

**Update configuration**:
```bash
# Regenerate configuration with all defaults
swg create config/existing.yml

# This updates missing parameters and recalculates hashes
```

**Manual parameter addition**:
```yaml
# Add missing parameters based on error messages
water:
  wave_height: 0.6        # Add if missing
  wave_period: 6.0        # Add if missing
  water_level: 1.0        # Add if missing
  water_density: 1000.0   # Add if missing
```

## Simulation Execution Issues

### SWASH Runtime Errors

#### NSTEMS Parameter Errors

**Symptoms**:
```bash
Error: Wrong type of data for variable NSTEMS
NSTEMS item read=10.0
```

**Solution**: This was a known issue that has been resolved in the framework. If you still encounter it:

```bash
# Ensure you're using the latest version
git pull
swg run config/test.yml  # Try again
```

**Manual fix** (if needed):
```yaml
# In configuration, ensure vegetation density is reasonable
vegetation:
  plant_density: 10       # Should be integer-like
```

#### Drag Coefficient Issues

**Symptoms**:
```bash
Severe error: No value for variable DRAG
```

**Solution**: Check vegetation configuration:
```yaml
vegetation:
  enable: true
  plant_height: 0.5
  plant_diameter: 0.01
  plant_density: 10
  drag_coefficient: 1.0   # Ensure this is present
```

#### Grid Resolution Problems

**Symptoms**:
```bash
Error: Grid spacing too large for wavelength
Warning: CFL condition violated
```

**Solutions**:

**Increase grid resolution**:
```yaml
grid:
  nx_cells: 1000          # Double resolution
  # or
  length: 56.0            # Reduce domain size
```

**Check wavelength vs. grid spacing**:
```python
# Calculate wavelength for your conditions
import numpy as np

T = 6.0      # Wave period
h = 1.0      # Water depth
g = 9.81

# Deep water approximation
L0 = g * T**2 / (2 * np.pi)

# Intermediate water (iterative solution)
k = 2 * np.pi / L0  # Initial guess
for _ in range(10):
    L = 2 * np.pi / k
    k = 2 * np.pi / L * np.sqrt(np.tanh(k * h))

print(f"Wavelength: {L:.2f} m")

# Check grid resolution
dx = 112.0 / 500  # Current resolution
print(f"Grid spacing: {dx:.3f} m")
print(f"Points per wavelength: {L/dx:.1f}")
print("Minimum 20 points per wavelength recommended")
```

### Memory and Performance Issues

#### Out of Memory Errors

**Symptoms**:
```bash
MemoryError: Unable to allocate array
OSError: [Errno 12] Cannot allocate memory
```

**Solutions**:

**Reduce memory usage**:
```yaml
# Coarser grid
grid:
  nx_cells: 250           # Half resolution
  n_layers: 2             # Minimum layers

# Shorter simulation
numeric:
  n_waves: 25             # Fewer waves

# Less frequent output
numeric:
  output_interval: 0.2    # Lower frequency
```

**Monitor memory usage**:
```bash
# Check memory during simulation
top -p $(pgrep swash)
htop

# Check available memory
free -h
```

#### Slow Simulation Performance

**Symptoms**:
- Simulation takes much longer than expected
- Progress updates are infrequent

**Optimization strategies**:

**Reduce computational load**:
```yaml
# Start with coarse simulation for testing
grid:
  nx_cells: 200           # Coarse grid
  n_layers: 2             # Minimum layers

numeric:
  n_waves: 20             # Short simulation
  time_step: 0.1          # Larger initial time step
```

**Monitor performance**:
```bash
# Watch simulation progress
tail -f simulations/test_12345/PRINT

# Check CPU usage
top
htop

# Estimate completion time
# Count progress lines and extrapolate
```

### File and Permission Issues

#### Permission Denied Errors

**Symptoms**:
```bash
PermissionError: [Errno 13] Permission denied: 'simulations/test_12345'
OSError: [Errno 13] Permission denied: 'config/test.yml'
```

**Solutions**:

**Check and fix permissions**:
```bash
# Check permissions
ls -la simulations/
ls -la config/

# Fix directory permissions
chmod 755 simulations/
chmod 644 config/*.yml

# Create directories if needed
mkdir -p simulations/
mkdir -p config/
```

**Run with appropriate permissions**:
```bash
# If installation requires sudo
sudo swg run config/test.yml

# Or fix ownership
sudo chown -R $USER:$USER simulations/ config/
```

#### Disk Space Issues

**Symptoms**:
```bash
OSError: [Errno 28] No space left on device
```

**Solutions**:

**Check disk usage**:
```bash
df -h .                 # Check current directory
du -sh simulations/     # Check simulation directory size
```

**Clean up old simulations**:
```bash
# List simulation directories by size
du -sh simulations/*/ | sort -hr

# Remove old simulations (be careful!)
rm -rf simulations/old_*

# Archive important results
tar -czf important_results.tar.gz simulations/important_*
rm -rf simulations/important_*
```

**Reduce output size**:
```yaml
# Less frequent output
numeric:
  output_interval: 0.5    # Larger interval

# Shorter simulations
numeric:
  n_waves: 30             # Fewer waves
```

## Physical and Numerical Issues

### Unrealistic Results

#### Extremely Large Wave Heights

**Symptoms**:
- Wave heights > 10 m in small-scale simulation
- Velocities > 20 m/s
- Simulation diverges or becomes unstable

**Diagnosis**:
```python
# Check wave steepness
H = 0.6      # Wave height
T = 6.0      # Period
h = 1.0      # Depth
g = 9.81

# Calculate wavelength (intermediate water approximation)
L = g * T**2 / (2 * np.pi) * np.tanh(2 * np.pi * h / (g * T**2 / (2 * np.pi)))
steepness = H / L

print(f"Wave steepness: {steepness:.4f}")
if steepness > 0.1:
    print("Warning: Very steep waves, reduce H or increase T")
```

**Solutions**:

**Reduce wave steepness**:
```yaml
water:
  wave_height: 0.4        # Reduce height
  wave_period: 8.0        # Increase period
```

**Check boundary conditions**:
```yaml
# Ensure proper sponge layer in template
# Check that SPONGE EAST command is present
```

#### Non-physical Parameter Combinations

**Symptoms**:
- Waves breaking immediately at generation
- Negative water levels
- Structure completely submerged

**Common issues and fixes**:

**Freeboard problems**:
```yaml
# Problem: Structure always submerged
water:
  water_level: 3.0        # High water level
breakwater:
  crest_height: 2.0       # Low crest
  
# Solution: Adjust relative levels
water:
  water_level: 1.0        # Lower water level
breakwater:
  crest_height: 2.5       # Higher crest
```

**Geometry conflicts**:
```yaml
# Problem: Structure too wide for domain
grid:
  length: 50.0            # Short domain
numeric:
  breakwater_start_position: 45.0  # Late start
breakwater:
  crest_width: 10.0       # Wide crest
  
# Solution: Adjust proportions
grid:
  length: 112.0           # Longer domain
numeric:
  breakwater_start_position: 80.0   # Earlier start
breakwater:
  crest_width: 3.0        # Narrower crest
```

### Numerical Instability

#### CFL Violations

**Symptoms**:
```bash
Warning: CFL condition violated
Error: Time step became too small
```

**Solutions**:

**Reduce wave steepness**:
```yaml
water:
  wave_height: 0.4        # Smaller waves
  wave_period: 8.0        # Longer period
```

**Increase grid resolution**:
```yaml
grid:
  nx_cells: 1000          # Finer grid
```

**Adjust time stepping**:
```yaml
numeric:
  time_step: 0.01         # Smaller initial time step
```

#### Convergence Problems

**Symptoms**:
- Simulation runs but produces noisy results
- Large residuals in `norm_end` file
- Oscillating solutions

**Solutions**:

**Improve vertical resolution**:
```yaml
grid:
  n_layers: 3             # More layers
```

**Add numerical damping**:
```yaml
# Check INPUT template for proper settings
# BREAKING command should be present for n_layers <= 3
```

**Verify boundary conditions**:
- Ensure proper sponge layer length
- Check wave generation boundary type

## Data Analysis Issues

### Missing Output Files

#### Symptoms**:
- Expected `.dat` files not generated
- `final_state.mat` missing
- Incomplete time series

**Diagnosis**:
```bash
# Check if simulation completed
tail simulations/test_12345/PRINT | grep "STOP"

# Check for error messages
grep -i error simulations/test_12345/PRINT
cat simulations/test_12345/Errfile 2>/dev/null

# List generated files
ls -la simulations/test_12345/
```

**Solutions**:

**Re-run simulation**:
```bash
# Clean directory and re-run
rm -rf simulations/test_12345/
swg run config/test.yml
```

**Check configuration**:
```yaml
# Ensure gauge positions are within domain
numeric:
  wave_gauge_positions:
    - 20.0                # Must be < grid.length
    - 60.0
    - 80.0
    - 100.0               # Must be < grid.length (112.0)
```

### Corrupted Data Files

#### Symptoms**:
- Cannot load `.dat` files with NumPy
- Unrealistic data values
- Partial file contents

**Diagnosis**:
```python
import numpy as np

try:
    data = np.loadtxt('simulations/test_12345/wg01.dat')
    print(f"Shape: {data.shape}")
    print(f"Data range: [{np.min(data):.2e}, {np.max(data):.2e}]")
    print(f"Has NaN: {np.any(np.isnan(data))}")
    print(f"Has Inf: {np.any(np.isinf(data))}")
except Exception as e:
    print(f"Loading error: {e}")
```

**Solutions**:

**Re-run with different settings**:
```yaml
# More stable numerical settings
grid:
  n_layers: 2             # Conservative
numeric:
  time_step: 0.01         # Smaller time step
  output_interval: 0.2    # Less frequent output
```

**Check file integrity**:
```bash
# Check file size progression during simulation
watch "ls -lh simulations/test_12345/*.dat"

# Verify files are not zero-length
find simulations/test_12345/ -name "*.dat" -size 0
```

## Advanced Troubleshooting

### Debug Mode Operation

#### Enable Detailed Logging
```python
# Modify simulation.py for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints in simulation functions
def _create_input_file(...):
    print(f"Creating INPUT file with config: {config}")
    # ... existing code
```

#### Manual SWASH Execution
```bash
# Run SWASH manually for debugging
cd simulations/test_12345/
swash < INPUT > manual_output.log 2>&1

# Compare with framework execution
diff PRINT manual_output.log
```

### Configuration Debugging

#### Dump Effective Configuration
```python
# Check final configuration values
from src.config import read_config
import json

config = read_config('config/test.yml')
print(json.dumps(config.model_dump(), indent=2))

# Check calculated properties
print(f"Simulation duration: {config.simulation_duration}")
print(f"Breakwater end: {config.breakwater_end_position}")
```

#### Template Variable Inspection
```python
# Debug template rendering
from jinja2 import Template
from src.config import read_config

config = read_config('config/test.yml')
with open('templates/INPUT') as f:
    template = Template(f.read())

# Check specific variables
print(f"Grid length: {config.grid.length}")
print(f"Wave height: {config.water.wave_height}")
print(f"Vegetation enabled: {config.vegetation.enable}")

# Render small sections for debugging
test_template = Template("{{ grid.length }} {{ grid.nx_cells }}")
print(test_template.render(grid=config.grid))
```

### Performance Profiling

#### Execution Timing
```bash
# Time complete workflow
time swg run config/test.yml

# Profile specific components
time swash < INPUT  # SWASH execution only
```

#### Memory Profiling
```python
# Monitor memory usage
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB")

# Call before/after major operations
monitor_memory()
# ... run simulation
monitor_memory()
```

## Getting Help

### Information to Provide

When seeking help, include:

1. **System information**:
   ```bash
   uname -a                    # Operating system
   python --version            # Python version
   swash --version            # SWASH version (if available)
   swg --version              # Framework version
   ```

2. **Configuration file**:
   ```bash
   cat config/problematic.yml
   ```

3. **Error messages**:
   ```bash
   # Complete error output
   swg run config/test.yml 2>&1 | tee error_log.txt
   
   # SWASH errors
   cat simulations/test_12345/Errfile
   grep -i error simulations/test_12345/PRINT
   ```

4. **File listings**:
   ```bash
   ls -la simulations/test_12345/
   du -sh simulations/test_12345/
   ```

### Resources

- **Framework documentation**: This documentation set
- **SWASH manual**: `docs/swash_manual.md`
- **SWASH website**: [http://swash.sourceforge.net/](http://swash.sourceforge.net/)
- **GitHub issues**: Create issues for framework-specific problems

### Self-Help Checklist

Before asking for help:

1. ✅ **Read error messages carefully**
2. ✅ **Check this troubleshooting guide**
3. ✅ **Verify configuration file syntax**
4. ✅ **Test with minimal example**
5. ✅ **Check file permissions and disk space**
6. ✅ **Try with default parameters**
7. ✅ **Search documentation for keywords**

---

## Summary of Common Solutions

| Problem | Quick Solution |
|---------|----------------|
| SWASH not found | `export PATH=$PATH:/path/to/swash` |
| YAML syntax error | Check indentation and colons |
| Parameter type error | Use correct types (int, float, bool) |
| Missing parameters | Run `swg create config/file.yml` |
| Permission denied | `chmod 755 simulations/` |
| Out of memory | Reduce `nx_cells` and `n_waves` |
| Unrealistic results | Check wave steepness H/L < 0.1 |
| Slow simulation | Reduce grid resolution for testing |
| Missing output | Check PRINT file for errors |
| Corrupted data | Re-run with smaller time step |

For issues not covered here, create a minimal reproduction case and consult the framework documentation or seek community help.