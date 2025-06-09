# SWASH Breakwater Modeling Framework Overview

## Introduction

This documentation describes a comprehensive framework for modeling vegetated breakwaters using SWASH (Simulating WAves till SHore) - a state-of-the-art numerical model for coastal wave propagation and transformation. The framework was developed to support coastal engineering research and design, particularly for nature-based coastal protection solutions.

## What is SWASH?

SWASH is a numerical wave model developed at Delft University of Technology that solves the non-hydrostatic shallow water equations. It is specifically designed for:

- **Wave propagation** from deep water to shore
- **Wave transformation** over complex bathymetry and structures  
- **Wave-structure interaction** including overtopping and transmission
- **Non-hydrostatic effects** important for short waves and steep slopes
- **Vegetation modeling** for nature-based coastal protection

### Key Capabilities

- **1D and 2D simulations** with adaptive vertical layering
- **Non-hydrostatic pressure** for accurate wave modeling
- **Porous structure modeling** for breakwaters and reefs
- **Vegetation drag forces** for coastal vegetation
- **Wave generation and absorption** boundaries
- **Comprehensive output** including time series and spatial fields

## Project Context: Baie-des-Bacon Breakwaters

This framework was developed to model living breakwaters designed for Baie-des-Bacon, Québec - a coastal protection project featuring:

- **Low-crested rubble mound breakwaters** with vegetation on the crest
- **Wave energy dissipation** through both structural porosity and vegetation drag
- **Nature-based coastal protection** combining engineering and ecological benefits
- **Climate adaptation** strategies for rising sea levels

### Physical Problem

The breakwaters are designed to:

1. **Reduce wave transmission** to protect the shoreline behind
2. **Limit wave overtopping** during storm events  
3. **Provide habitat** for coastal vegetation
4. **Maintain navigation** while offering protection

## Framework Architecture

This modeling framework consists of several integrated components:

### 1. Configuration System
- **Hierarchical YAML configuration** with automatic validation
- **Parameter grouping** by physical domains (water, breakwater, vegetation, etc.)
- **Hash-based reproducibility** for simulation tracking
- **Template-driven input generation** using Jinja2

### 2. Simulation Engine
- **Automated file generation** (bathymetry, porosity, structure height)
- **SWASH execution management** with error handling
- **Result processing** and validation
- **Parallel execution** support for parameter studies

### 3. Command Line Interface
- **Simple commands** for creating and running simulations
- **Glob pattern support** for batch processing
- **Interactive dashboard** for visualization (in development)

## Model Setup Overview

The framework models a **1D wave channel experiment** representing:

### Physical Domain
- **112m long channel** with regular grid spacing
- **Flat bottom bathymetry** for controlled conditions
- **Breakwater positioned** at x = 100m from wave generation
- **Wave gauges** positioned upstream, on, and downstream of structure

### Breakwater Structure  
- **Trapezoidal cross-section** with specified crest width and slopes
- **Porous media representation** using SWASH's porosity module
- **Variable structure height** from base to crest
- **Optional vegetation** on the breakwater crest

### Wave Conditions
- **Regular wave generation** with specified height and period
- **Weakly reflective boundaries** to minimize reflection
- **Sponge layer** at downstream end for wave absorption
- **Parametric wave conditions** for systematic studies

## Key Features

### 1. Physically-Based Modeling
- **Non-hydrostatic wave dynamics** for accurate short-wave modeling
- **Porous media flow** through breakwater structure
- **Vegetation drag forces** using established formulations
- **Wave breaking** and energy dissipation

### 2. Flexible Configuration
- **Modular parameter organization** for easy modification
- **Template-based input generation** for consistent setup
- **Automatic validation** to prevent configuration errors
- **Version control friendly** YAML format

### 3. Reproducible Science
- **Configuration hashing** for unique experiment identification
- **Automated directory structure** for organized results
- **Error checking** and validation throughout the workflow
- **Version tracking** of all parameters and settings

### 4. Vegetation Modeling
- **Spatially-varying vegetation** placed only on breakwater crest
- **Automatic crest zone calculation** from structure geometry
- **Physically-based drag coefficients** from literature
- **Seasonal variations** (with/without foliage)
- **Integration with structure porosity** effects

## Applications

This framework supports various coastal engineering applications:

### Research Applications
- **Wave-vegetation interaction** studies
- **Breakwater optimization** for different wave conditions
- **Climate change impact** assessment
- **Nature-based solution** effectiveness quantification

### Design Applications  
- **Structure sizing** and optimization
- **Overtopping assessment** for different freeboard scenarios
- **Vegetation species selection** based on drag characteristics
- **Cost-benefit analysis** of green infrastructure

### Validation Studies
- **Physical model comparison** with laboratory experiments
- **Field data validation** when available
- **Benchmark studies** against analytical solutions
- **Sensitivity analysis** for parameter uncertainty

## Next Steps

To get started with this framework:

1. **Review the [Breakwater Design Guide](breakwater-design.md)** to understand the physical structure
2. **Explore the [Configuration Guide](configuration-guide.md)** to learn about parameter setup
3. **Read the [Simulation Workflow](simulation-workflow.md)** to run your first simulation
4. **Study the [INPUT File Reference](input-file-reference.md)** for detailed SWASH setup

For troubleshooting and advanced topics, see the specialized guides for physics, outputs, and common issues.