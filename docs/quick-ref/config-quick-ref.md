# Configuration Quick Reference

## Essential Parameters

| Parameter | Default | Range | Unit | Description |
|-----------|---------|-------|------|-------------|
| `name` | *required* | - | - | Experiment name |
| `water.water_level` | 1.0 | >0 | m | Still water level |
| `water.wave_height` | 0.5 | >0 | m | Wave height |
| `water.wave_period` | 6.0 | >0 | s | Wave period |

## Breakwater Parameters

| Parameter | Default | Range | Unit | Description |
|-----------|---------|-------|------|-------------|
| `breakwater.enable` | true | - | - | Enable breakwater |
| `breakwater.crest_height` | 2.0 | >0 | m | Height above seafloor |
| `breakwater.crest_length` | 2.0 | >0 | m | Crest length |
| `breakwater.slope` | 2.0 | >0 | - | Side slope (H:V) |
| `breakwater.porosity` | 0.4 | 0-1 | - | Porosity coefficient |
| `breakwater.armour_dn50` | 1.150 | >0 | m | Stone diameter |
| `breakwater.breakwater_start_position` | 70.0 | 0-112 | m | X-position |

## Vegetation Parameters

| Parameter | Default | Range | Unit | Description |
|-----------|---------|-------|------|-------------|
| `vegetation.enable` | false | - | - | Enable vegetation |
| `vegetation.type.plant_height` | 0.5 | >0 | m | Plant height |
| `vegetation.type.plant_diameter` | 0.01 | >0 | m | Stem diameter |
| `vegetation.type.plant_density` | 1.0 | >0 | 1/m² | Stem density |
| `vegetation.type.drag_coefficient` | 1.0 | >0 | - | Drag coefficient |
| `vegetation.distribution` | "half" | half/alternating | - | Spatial pattern |
| `vegetation.type_fraction` | 0.5 | 0-1 | - | Primary type fraction |

## Numeric Parameters

| Parameter | Default | Range | Unit | Description |
|-----------|---------|-------|------|-------------|
| `numeric.n_waves` | 50 | >0 | - | Number of wave periods |
| `numeric.wave_gauge_positions` | [20,60,65,80,100] | 0-112 | m | Gauge X-positions |

## Fixed Parameters

| Parameter | Value | Unit | Description |
|-----------|--------|------|-------------|
| Domain length | 112.0 | m | Total channel length |
| Grid cells | 500 | - | Spatial resolution |
| Grid spacing | 0.224 | m | Δx resolution |
| Vertical layers | 2 | - | Vertical discretization |
| Time step | 0.05 | s | Initial time step |
| Output interval | 0.1 | s | Data sampling rate |

## Typical Value Ranges

### Wave Conditions
- **Shallow water**: H/h < 0.3, T = 4-8s
- **Intermediate**: H/h = 0.3-0.6, T = 6-12s  
- **Breaking limit**: H/h < 0.8

### Breakwater Design
- **Low-crested**: crest_height = 0.5-1.5 × water_level
- **Emergent**: crest_height = 1.2-2.0 × water_level
- **Slope**: 1.5-3.0 (typical: 2.0)
- **Porosity**: 0.3-0.5 (rubble mound)

### Vegetation Properties  
- **Marsh grass**: height=0.3-1.0m, diameter=0.005-0.02m
- **Shrubs**: height=0.5-2.0m, diameter=0.01-0.05m
- **Density**: 10-1000 stems/m²
- **Drag**: 0.5-2.0 (typical: 1.0)

## Common Configurations

### Basic Breakwater
```yaml
name: "basic_breakwater"
water:
  water_level: 1.0
  wave_height: 0.4
  wave_period: 6.0
breakwater:
  enable: true
  crest_height: 1.5
  porosity: 0.4
vegetation:
  enable: false
```

### Vegetated Breakwater
```yaml
name: "vegetated_breakwater"
breakwater:
  enable: true
vegetation:
  enable: true
  type:
    plant_height: 0.8
    plant_density: 100.0
```

### High Energy Waves
```yaml
name: "high_energy"
water:
  wave_height: 0.8
  wave_period: 8.0
breakwater:
  crest_height: 2.5
  armour_dn50: 2.0
```

## Quick Validation

✅ **Valid ranges:**
- H/h < 0.8 (avoid excessive breaking)
- Breakwater height > 0.5 × water_level
- Wave gauge positions within 0-112m
- Porosity between 0.3-0.5

⚠️ **Common issues:**
- Very short periods (T < 4s) may need finer grid
- Very high waves (H > 1m) may cause instability  
- Vegetation without breakwater won't work