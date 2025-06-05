# SWASH Breakwater Modeling Framework Documentation

## Overview

This comprehensive documentation describes a framework for modeling vegetated breakwaters using SWASH (Simulating WAves till SHore). The framework provides a complete workflow from configuration management to result analysis, specifically designed for nature-based coastal protection research.

## Documentation Structure

The documentation is organized into focused guides that can be read sequentially or referenced independently:

### 🚀 Getting Started

1. **[SWASH Overview](swash-overview.md)**
   - Introduction to SWASH and the modeling framework
   - Project context: Baie-des-Bacon breakwaters
   - Framework architecture and key features
   - **Start here** for project context and overview

2. **[Breakwater Design](breakwater-design.md)**
   - Physical structure being modeled
   - Geometric parameters and material properties
   - Vegetation characteristics and placement
   - Real-world application context

### ⚙️ Configuration and Setup

3. **[Configuration Guide](configuration-guide.md)**
   - Hierarchical parameter organization
   - YAML configuration management
   - Parameter validation and defaults
   - **Essential** for setting up simulations

4. **[Simulation Workflow](simulation-workflow.md)**
   - Command-line interface usage
   - Step-by-step execution process
   - Batch processing and parameter studies
   - **Practical guide** for running simulations

### 🔧 Technical Reference

5. **[INPUT File Reference](input-file-reference.md)**
   - Detailed SWASH input file structure
   - Template system and Jinja2 processing
   - Hard-coded vs. configurable parameters
   - **In-depth technical** reference

6. **[Physics and Parameters](physics-and-parameters.md)**
   - Physical principles and theory
   - Parameter meanings and relationships
   - Dimensional analysis and scaling
   - **Scientific foundation** for modeling choices

### 📊 Results and Analysis

7. **[Output Reference](output-reference.md)**
   - SWASH output file formats
   - Time series and spatial data analysis
   - Data loading and visualization examples
   - **Complete guide** to interpreting results

8. **[Troubleshooting](troubleshooting.md)**
   - Common issues and solutions
   - Diagnostic procedures
   - Performance optimization
   - **Problem-solving** resource

## Quick Navigation by Task

### First-Time Users
1. Read [SWASH Overview](swash-overview.md) for context
2. Review [Breakwater Design](breakwater-design.md) for physical understanding
3. Follow [Simulation Workflow](simulation-workflow.md) to run your first simulation

### Setting Up New Studies
1. Use [Configuration Guide](configuration-guide.md) for parameter setup
2. Reference [Physics and Parameters](physics-and-parameters.md) for parameter selection
3. Apply [Simulation Workflow](simulation-workflow.md) for execution

### Understanding Results
1. Consult [Output Reference](output-reference.md) for file formats
2. Apply analysis techniques from the output guide
3. Use [Physics and Parameters](physics-and-parameters.md) for physical interpretation

### Solving Problems
1. Check [Troubleshooting](troubleshooting.md) for common issues
2. Reference technical guides for specific components
3. Verify configuration using the configuration guide

### Advanced Development
1. Study [INPUT File Reference](input-file-reference.md) for template modification
2. Use [Physics and Parameters](physics-and-parameters.md) for new parameter implementation
3. Reference all guides for comprehensive understanding

## Documentation Features

### 🎯 Practical Examples
- Complete code examples in Python and MATLAB
- Real configuration files and parameter sets
- Step-by-step procedures with command-line examples

### 🔗 Cross-References
- Consistent linking between related topics
- "Next Steps" sections guiding readers to relevant material
- Comprehensive index of topics and concepts

### 📋 Reference Tables
- Parameter descriptions with units and defaults
- File format specifications
- Troubleshooting quick reference

### 🧮 Technical Details
- Mathematical formulations and theory
- Physical principles and assumptions
- Implementation details and limitations

## Framework Components Overview

### Configuration System
```yaml
# Hierarchical YAML configuration
grid:           # Computational domain
breakwater:     # Structure geometry  
water:          # Wave conditions
vegetation:     # Plant characteristics
numeric:        # Simulation control
```

### Execution Workflow
```
Configuration → File Generation → SWASH Execution → Result Collection
     ↓              ↓               ↓                ↓
   YAML files → INPUT + data → Time series + → Analysis
                  files        spatial fields    tools
```

### Key Capabilities
- **Automated file generation**: Bathymetry, porosity, structure height
- **Template-based INPUT**: Jinja2 templating for SWASH input files
- **Vegetation modeling**: Spatial vegetation distributions on breakwater crest
- **Parameter validation**: Type checking and physical constraints
- **Reproducible research**: Configuration hashing and version control

## Physical Modeling Scope

### Wave Conditions
- **Regular waves**: Systematic parameter studies
- **Intermediate water**: Typical coastal conditions (h/L = 0.05-0.5)
- **Non-hydrostatic**: Accurate short-wave modeling

### Structure Types
- **Low-crested breakwaters**: Submerged and emergent conditions
- **Rubble mound construction**: Porous media representation
- **Vegetated crest**: Nature-based coastal protection

### Analysis Capabilities
- **Wave transmission**: Energy dissipation quantification
- **Overtopping analysis**: Discharge estimation
- **Vegetation effects**: Drag force impact assessment
- **Setup analysis**: Mean water level changes

## Research Applications

### Coastal Engineering
- Breakwater design optimization
- Overtopping assessment for different sea levels
- Climate change adaptation strategies
- Cost-benefit analysis of green infrastructure

### Scientific Research
- Wave-vegetation interaction mechanisms
- Porous media flow validation
- Physical model comparison
- Scaling law verification

### Educational Use
- Coastal engineering pedagogy
- Numerical modeling training
- Parameter sensitivity demonstration
- Physical process visualization

## System Requirements

### Software Dependencies
- **SWASH**: Wave modeling engine (separate installation required)
- **Python 3.13+**: Framework runtime environment
- **Key packages**: Pydantic, Jinja2, NumPy, ruamel.yaml

### Hardware Requirements
- **Memory**: 4-8 GB RAM for typical simulations
- **Storage**: 1-10 GB per parameter study
- **CPU**: Single-core SWASH execution (parallel studies possible)

### Operating Systems
- **Linux**: Primary development and testing platform
- **macOS**: Compatible with framework and SWASH
- **Windows**: Compatible (may require additional setup)

## Getting Help and Support

### Self-Help Resources
1. **This documentation**: Comprehensive coverage of all topics
2. **Configuration examples**: Working examples in `config/` directory
3. **Error messages**: Detailed diagnostics and suggestions

### Community Resources
- **GitHub repository**: Source code and issue tracking
- **SWASH community**: Official SWASH documentation and forums

### Reporting Issues
When reporting problems, please include:
- Configuration file used
- Complete error messages
- System information (OS, Python version, SWASH version)
- Steps to reproduce the issue

## Contributing to Documentation

### Improvement Suggestions
- Identify unclear sections or missing information
- Suggest additional examples or use cases
- Report documentation errors or inconsistencies

### Technical Contributions
- Framework enhancements and bug fixes
- New analysis tools and visualization methods
- Additional physical modeling capabilities

## Version and Maintenance

This documentation is maintained alongside the framework source code:
- **Version control**: Synchronized with code development
- **Regular updates**: Reflects latest features and fixes
- **Community feedback**: Incorporates user suggestions and clarifications

---

## Quick Start Guide

### 1. Installation
```bash
# Clone repository and install
git clone <repository-url>
cd simulations
uv sync  # or pip install -e .
```

### 2. First Simulation
```bash
# Create configuration
swg create config/my_first.yml

# Run simulation  
swg run config/my_first.yml

# Check results
ls simulations/my_first_*/
```

### 3. Basic Analysis
```python
import numpy as np
data = np.loadtxt('simulations/my_first_*/wg01.dat')
time, eta, u = data.T
print(f"Max wave height: {np.max(eta) - np.min(eta):.3f} m")
```

### 4. Next Steps
- Explore [Configuration Guide](configuration-guide.md) to modify parameters
- Read [Physics and Parameters](physics-and-parameters.md) to understand the modeling
- Use [Output Reference](output-reference.md) for detailed analysis

---

**Happy modeling!** 🌊

*This documentation provides everything needed to successfully use the SWASH breakwater modeling framework for research, engineering, and educational applications.*