---
layout: default
title: "SWASH Breakwater Framework Documentation"
description: "Complete documentation for modeling vegetated breakwaters using SWASH"
---

# SWASH Breakwater Modeling Framework

A comprehensive framework for modeling vegetated breakwaters using SWASH (Simulating WAves till SHore), specifically designed for nature-based coastal protection research.

## Quick Start

New to the framework? Start here:

1. **[SWASH Overview](swash-overview)** - Understand the project and framework
2. **[Simulation Workflow](simulation-workflow)** - Run your first simulation
3. **[Configuration Guide](configuration-guide)** - Set up your parameters

## Documentation Guides

### 🚀 Getting Started
- **[SWASH Overview](swash-overview)** - Project context and framework introduction
- **[Breakwater Design](breakwater-design)** - Physical structure details
- **[Simulation Workflow](simulation-workflow)** - Step-by-step execution guide

### ⚙️ Configuration & Setup
- **[Configuration Guide](configuration-guide)** - Parameter management and validation
- **[Physics and Parameters](physics-and-parameters)** - Scientific foundation and parameter meanings

### 🔧 Technical Reference
- **[INPUT File Reference](input-file-reference)** - SWASH input file structure and templates
- **[Output Reference](output-reference)** - Result analysis and data formats

### 🛠️ Support
- **[Troubleshooting](troubleshooting)** - Common issues and solutions

## Key Features

- **Interactive Dashboard**: Visual configuration management
- **CLI Interface**: Command-line tools for batch processing
- **Template System**: Automated SWASH input file generation
- **Vegetation Modeling**: Spatial vegetation distributions
- **Reproducible Research**: Configuration hashing and validation

## Research Applications

### Coastal Engineering
- Breakwater design optimization
- Wave transmission analysis
- Overtopping assessment
- Climate adaptation strategies

### Scientific Research
- Wave-vegetation interactions
- Porous media flow validation
- Physical model comparisons
- Scaling law verification

## Quick Example

```bash
# Create configuration
python -m src.cli create config/my-study.yml

# Run simulation
python -m src.cli run config/my-study.yml

# Launch dashboard
python -m src.cli dashboard
```

## System Requirements

- **Python 3.13+** and **SWASH** numerical model
- **Memory**: 4-8 GB RAM for typical simulations
- **Platforms**: Linux (primary), macOS, Windows

---

Ready to get started? Begin with the **[SWASH Overview](swash-overview)** to understand the framework, then follow the **[Simulation Workflow](simulation-workflow)** to run your first simulation.