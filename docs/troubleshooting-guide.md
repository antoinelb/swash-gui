# Troubleshooting Guide

This guide helps diagnose and resolve common issues encountered when using SWASH simulations. Issues are organized by category with specific symptoms, causes, and solutions.

## Installation and Setup Issues

### SWASH Not Found

**Symptoms:**
- `swash: command not found` error
- `FileNotFoundError` when running simulations
- CLI shows SWASH installation warnings

**Causes:**
- SWASH not installed or not in system PATH
- Incorrect SWASH executable name (e.g., `swash.exe` on Windows)

**Solutions:**

1. **Install SWASH:**
   ```bash
   # Download from https://swash.sourceforge.io/download/
   # Follow platform-specific installation instructions
   ```

2. **Add to PATH:**
   ```bash
   # Linux/macOS - add to ~/.bashrc or ~/.zshrc
   export PATH="/path/to/swash:$PATH"
   
   # Windows - add SWASH directory to system PATH
   ```

3. **Verify Installation:**
   ```bash
   swash --version
   # Should show: SWASH version 11.01A or similar
   ```

### Python Dependencies Issues

**Symptoms:**
- Import errors when running CLI
- Missing module errors
- Version compatibility warnings

**Solutions:**

1. **Install with uv (recommended):**
   ```bash
   uv sync
   ```

2. **Install with pip:**
   ```bash
   pip install -e .
   ```

3. **Check Python version:**
   ```bash
   python --version  # Should be 3.13+
   ```

## Configuration Issues

### Invalid YAML Syntax

**Symptoms:**
- `yaml.scanner.ScannerError` when loading config
- Parsing errors mentioning line numbers
- Configuration not loading in dashboard

**Common Causes:**
```yaml
# Incorrect indentation
water:
water_level: 1.0  # Should be indented

# Missing quotes for strings with special characters
name: test:experiment  # Should be: name: "test:experiment"

# Invalid values
breakwater:
  enable: yes  # Should be: true or false
```

**Solutions:**

1. **Use proper YAML indentation (2 spaces):**
   ```yaml
   water:
     water_level: 1.0
     wave_height: 0.5
   ```

2. **Validate YAML syntax:**
   ```bash
   # Use online validator or
   python -c "import yaml; yaml.safe_load(open('config.yml'))"
   ```

3. **Use dashboard for guided editing** - prevents syntax errors

### Parameter Validation Errors

**Symptoms:**
- `ValidationError` from Pydantic
- "Value error" messages with parameter details
- Configuration rejected during loading

**Common Issues:**

```python
# Out of range values
vegetation.type_fraction: 1.5  # Must be 0.0-1.0

# Negative physical parameters
water.wave_height: -0.5  # Must be positive

# Wrong parameter type
numeric.n_waves: "fifty"  # Must be integer
```

**Solutions:**

1. **Check parameter ranges** in [Configuration Reference](configuration-reference.md)
2. **Use dashboard validation** - shows errors immediately
3. **Check units** - ensure consistent unit system (meters, seconds)

### Missing Required Parameters

**Symptoms:**
- "Field required" validation errors
- Configuration won't save or load
- Missing sections in generated INPUT

**Solutions:**

1. **Ensure name is specified:**
   ```yaml
   name: "experiment_name"  # Always required
   ```

2. **Use complete config template:**
   ```bash
   swg create config/new-experiment.yml
   ```

3. **Check all sections are present** - see example configs in `config/`

## Simulation Runtime Issues

### SWASH Execution Errors

**Symptoms:**
- Simulation exits immediately
- Error messages in PRINT file
- No output files generated

**Common SWASH Errors:**

**"IRREGULAR CONDITIONS":**
```
*** ERROR: IRREGULAR CONDITIONS ***
```
- **Cause:** Numerical instability, typically CFL violation
- **Solution:** 
  - Reduce initial time step in template (current: 0.05s)
  - Check for extreme parameter values
  - Review grid resolution adequacy

**"POROSITY VALUES OUT OF RANGE":**
```
*** ERROR: POROSITY VALUES OUT OF RANGE ***
```
- **Cause:** Porosity values outside 0.0-1.0 range
- **Solution:**
  - Check `breakwater.porosity` parameter (typical: 0.3-0.5)
  - Verify porosity file generation

**"NEGATIVE WATER DEPTHS":**
```
*** ERROR: NEGATIVE WATER DEPTHS ***
```
- **Cause:** Bathymetry issues or extreme setup
- **Solution:**
  - Check water level vs. breakwater height
  - Verify bathymetry file is reasonable
  - Ensure adequate water depth everywhere

### Grid Resolution Issues

**Symptoms:**
- Poor wave representation
- Numerical dispersion errors
- Inaccurate wave heights

**Diagnostics:**
- **Wavelength:** L = gT²/(2π) in deep water
- **Grid requirement:** Δx < L/20 (ideally L/25-30)
- **Current grid:** Δx = 0.224m (112m / 500 cells)

**Solutions:**

1. **For short waves (T < 4s):**
   - May need finer grid resolution
   - Consider increasing nx_cells in config

2. **For long waves (T > 10s):**
   - Current resolution adequate
   - Check time step adequacy

### Time Step and Stability

**Symptoms:**
- Simulation crashes mid-run
- "OVERFLOW" or "UNDERFLOW" errors
- Extremely slow convergence

**CFL Condition Check:**
- **Stability criterion:** Δt < Δx/√(gh)
- **Current:** Δt = 0.05s, Δx = 0.224m, h ≈ 1m
- **Max stable:** Δt < 0.224/√(9.81×1) ≈ 0.071s ✓

**Solutions:**

1. **Reduce initial time step** in template:
   ```
   COMPUTE 000000.000 0.02 SEC {{ simulation_duration }}
   ```

2. **Check extreme parameter combinations:**
   - Very high waves (H/h > 0.8)
   - Very short periods (T < 3s)
   - Extreme breakwater geometry

### Memory and Performance Issues

**Symptoms:**
- Very slow simulation progress
- System memory exhaustion
- Simulation never completes

**Solutions:**

1. **Reduce simulation duration:**
   ```yaml
   numeric:
     n_waves: 20  # Instead of 50 for testing
   ```

2. **Monitor system resources:**
   ```bash
   htop  # Check CPU and memory usage
   ```

3. **Optimize grid if needed:**
   - Current 500 cells should be manageable
   - Consider computational resources available

## Output and Analysis Issues

### Missing Output Files

**Symptoms:**
- No wgXX.txt files generated
- Empty simulation directory
- final_state.mat missing

**Causes and Solutions:**

1. **Simulation didn't complete successfully:**
   - Check PRINT file for errors
   - Look for early termination messages
   - Review SWASH execution log

2. **Wave gauge positions outside domain:**
   ```yaml
   numeric:
     wave_gauge_positions: [150.0]  # Outside 0-112m domain
   ```
   - Ensure all positions are 0.0 ≤ x ≤ 112.0

3. **Incorrect file permissions:**
   ```bash
   chmod -R 755 simulations/
   ```

### Incorrect Analysis Results

**Symptoms:**
- Unexpected wave heights
- Strange velocity patterns
- Analysis plots look wrong

**Diagnostics:**

1. **Check raw wave gauge data:**
   ```bash
   head simulations/*/swash/wg01.txt
   # Should show reasonable wave oscillations
   ```

2. **Verify configuration mapping:**
   - Compare INPUT file with intended config
   - Check template rendering worked correctly

3. **Review PRINT file:**
   - Look for warnings about model setup
   - Check convergence messages

### Analysis Module Errors

**Symptoms:**
- Analysis fails to run
- Missing plots or JSON files
- Python errors during post-processing

**Solutions:**

1. **Check required output files exist:**
   ```bash
   ls simulations/*/swash/wg*.txt
   ```

2. **Run analysis manually:**
   ```bash
   swg analyze config/experiment.yml
   ```

3. **Check analysis dependencies:**
   ```bash
   python -c "import matplotlib, plotly, pandas"
   ```

## Physical Result Issues

### Unrealistic Wave Heights

**Symptoms:**
- Wave heights much larger or smaller than expected
- No wave attenuation across breakwater
- Extreme wave amplification

**Physical Checks:**

1. **Breaking criterion:**
   - H/h < 0.8 for stability
   - Current breaking: γ = 0.6

2. **Reflection effects:**
   - Standing waves can double wave heights
   - Check upstream wave gauge patterns

3. **Structure effectiveness:**
   - Kt ≈ 0.3-0.7 typical for rubble breakwaters
   - Zero transmission indicates blocked flow

**Solutions:**

1. **Adjust wave conditions:**
   ```yaml
   water:
     wave_height: 0.3  # Reduce if H/h > 0.5
   ```

2. **Check breakwater parameters:**
   - Porosity: 0.3-0.5 typical
   - Height: should be > still water level

### Vegetation Effects Not Visible

**Symptoms:**
- No difference between vegetated/non-vegetated cases
- Vegetation seems ineffective
- No additional dissipation

**Diagnostics:**

1. **Check vegetation density file:**
   ```bash
   head simulations/*/swash/vegetation_density.txt
   # Should show non-zero values on crest
   ```

2. **Verify vegetation parameters:**
   - Height: should be significant relative to water depth
   - Density: typical range 10-1000 stems/m²
   - Drag coefficient: 0.5-2.0 typical

**Solutions:**

1. **Increase vegetation density:**
   ```yaml
   vegetation:
     type:
       plant_density: 100.0  # Increase from default
   ```

2. **Check vegetation placement:**
   - Only active on breakwater crest
   - Requires `breakwater.enable: true`

## Dashboard and Interface Issues

### Dashboard Won't Start

**Symptoms:**
- Port already in use errors
- Dashboard crashes on startup
- Cannot connect to http://localhost:8000

**Solutions:**

1. **Check port availability:**
   ```bash
   lsof -i :8000  # Check what's using port 8000
   pkill -f dashboard  # Kill existing dashboard
   ```

2. **Use different port:**
   ```bash
   swg dashboard --port 8080
   ```

3. **Check firewall settings:**
   - Ensure localhost connections allowed
   - Try accessing via 127.0.0.1:8000

### Configuration Not Saving

**Symptoms:**
- Changes don't persist in dashboard
- YAML files not updated
- Configuration reverts to defaults

**Solutions:**

1. **Check file permissions:**
   ```bash
   chmod 644 config/*.yml
   ```

2. **Verify configuration syntax:**
   - Dashboard may silently reject invalid configs
   - Check browser console for errors

## Debugging Workflow

### Systematic Debugging Approach

1. **Check System Prerequisites:**
   ```bash
   swash --version    # SWASH installed
   swg --help         # CLI working
   python --version   # Python 3.13+
   ```

2. **Validate Configuration:**
   ```bash
   swg create config/debug.yml    # Create test config
   # Edit with minimal parameters
   swg run config/debug.yml       # Test run
   ```

3. **Check SWASH Execution:**
   ```bash
   # Look at PRINT file for errors
   tail -20 simulations/*/swash/PRINT
   
   # Check if files were generated
   ls -la simulations/*/swash/
   ```

4. **Verify Output Files:**
   ```bash
   # Check wave gauge files
   wc -l simulations/*/swash/wg*.txt
   
   # Look at first few lines
   head simulations/*/swash/wg01.txt
   ```

5. **Run Analysis:**
   ```bash
   swg analyze config/debug.yml
   ls simulations/*/analysis/
   ```

### Log Analysis

**PRINT File Interpretation:**
- **ITERATION**: Shows computational progress
- **TIME**: Current simulation time
- **WARNING**: Non-fatal issues to investigate
- **ERROR**: Fatal issues requiring fixing

**Common Warning Messages:**
- "BOTTOM FRICTION HIGH": May need to reduce friction
- "CFL NUMBER LARGE": Time step near stability limit
- "POROSITY INTERPOLATION": Structure definition issues

## Getting Help

### Information to Collect

When reporting issues, include:

1. **System Information:**
   - Operating system and version
   - Python version
   - SWASH version

2. **Configuration:**
   - Complete YAML configuration file
   - Generated INPUT file (if applicable)

3. **Error Messages:**
   - Complete error traceback
   - Relevant lines from PRINT file
   - Any warning messages

4. **Reproduction Steps:**
   - Exact commands run
   - Expected vs. actual behavior

### Resources

- **SWASH Documentation:** Complete manual in `docs/swash_manual/`
- **Framework Documentation:** [Overview](README.md), [Configuration](configuration-reference.md)
- **Example Configurations:** `config/` directory
- **Community:** SWASH user forums and mailing lists

## Next Steps

- [Configuration Reference](configuration-reference.md) - Parameter documentation
- [SWASH Physics](swash-physics.md) - Understanding the numerical model
- [Output Interpretation](output-interpretation.md) - Analyzing results