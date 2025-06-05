// Config viewer/editor component

import { debounce } from '../utils.js';

export function createConfigViewer(container, configStore, editable = false) {
  let unsubscribe = null;
  
  const createField = (label, value, path, type = 'number') => {
    const fieldId = path.replace(/\./g, '-');
    
    if (editable) {
      return `
        <div class="field">
          <label for="${fieldId}">${label}</label>
          <input 
            type="${type}"
            id="${fieldId}"
            value="${value}"
            data-path="${path}"
            ${type === 'number' ? 'step="0.01"' : ''}
          />
        </div>
      `;
    } else {
      return `
        <div class="field">
          <label>${label}</label>
          <span class="field-value">${value}</span>
        </div>
      `;
    }
  };
  
  const createArrayField = (label, values, path) => {
    const fieldId = path.replace(/\./g, '-');
    const valueStr = values.join(', ');
    
    if (editable) {
      return `
        <div class="field">
          <label for="${fieldId}">${label}</label>
          <input 
            type="text"
            id="${fieldId}"
            value="${valueStr}"
            data-path="${path}"
            data-array="true"
            placeholder="Comma-separated values"
          />
        </div>
      `;
    } else {
      return `
        <div class="field">
          <label>${label}</label>
          <span class="field-value">${valueStr}</span>
        </div>
      `;
    }
  };
  
  const createCheckbox = (label, value, path) => {
    const fieldId = path.replace(/\./g, '-');
    
    if (editable) {
      return `
        <div class="field">
          <label for="${fieldId}">${label}</label>
          <input 
            type="checkbox"
            id="${fieldId}"
            data-path="${path}"
            ${value ? 'checked' : ''}
          />
        </div>
      `;
    } else {
      return `
        <div class="field">
          <label>${label}</label>
          <span class="field-value">${value ? 'Enabled' : 'Disabled'}</span>
        </div>
      `;
    }
  };
  
  const render = (config) => {
    if (!config) return;
    
    container.innerHTML = `
      <h3>Configuration</h3>
      <div class="config-form">
        <section>
          <h3>General</h3>
          ${createField('Name', config.name, 'name', 'text')}
          ${!editable ? createField('Hash', config.hash?.substring(0, 8) || 'N/A', 'hash', 'text') : ''}
        </section>
        
        <section>
          <h3>Computational Grid</h3>
          ${createField('Domain Length (m)', config.grid.length, 'grid.length')}
          ${createField('Grid Cells (X)', config.grid.nx_cells, 'grid.nx_cells')}
          ${createField('Vertical Layers', config.grid.n_layers, 'grid.n_layers')}
        </section>
        
        <section>
          <h3>Breakwater</h3>
          ${createField('Crest Height (m)', config.breakwater.crest_height, 'breakwater.crest_height')}
          ${createField('Crest Width (m)', config.breakwater.crest_width, 'breakwater.crest_width')}
          ${createField('Slope (H:V ratio)', config.breakwater.slope, 'breakwater.slope')}
          ${createField('Porosity', config.breakwater.porosity, 'breakwater.porosity')}
          ${createField('Stone Density (kg/m³)', config.breakwater.stone_density, 'breakwater.stone_density')}
          ${createField('Armour Dn50 (m)', config.breakwater.armour_dn50, 'breakwater.armour_dn50')}
          ${createField('Filter Dn50 (m)', config.breakwater.filter_dn50, 'breakwater.filter_dn50')}
          ${createField('Core Dn50 (m)', config.breakwater.core_dn50, 'breakwater.core_dn50')}
        </section>
        
        <section>
          <h3>Water & Waves</h3>
          ${createField('Water Level (m)', config.water.water_level, 'water.water_level')}
          ${createField('Water Density (kg/m³)', config.water.water_density, 'water.water_density')}
          ${createField('Wave Height (m)', config.water.wave_height, 'water.wave_height')}
          ${createField('Wave Period (s)', config.water.wave_period, 'water.wave_period')}
        </section>
        
        <section>
          <h3>Vegetation</h3>
          ${createCheckbox('Enable Vegetation', config.vegetation.enable, 'vegetation.enable')}
          ${createField('Plant Height (m)', config.vegetation.plant_height, 'vegetation.plant_height')}
          ${createField('Plant Diameter (m)', config.vegetation.plant_diameter, 'vegetation.plant_diameter')}
          ${createField('Plant Density (/m²)', config.vegetation.plant_density, 'vegetation.plant_density')}
          ${createField('Drag Coefficient', config.vegetation.drag_coefficient, 'vegetation.drag_coefficient')}
        </section>
        
        <section>
          <h3>Numerical Parameters</h3>
          ${createField('Number of Waves', config.numeric.n_waves, 'numeric.n_waves')}
          ${createField('Time Step (s)', config.numeric.time_step, 'numeric.time_step')}
          ${createField('Breakwater Start Position (m)', config.numeric.breakwater_start_position, 'numeric.breakwater_start_position')}
          ${createField('Output Interval (s)', config.numeric.output_interval, 'numeric.output_interval')}
          ${createArrayField('Wave Gauge Positions (m)', config.numeric.wave_gauge_positions, 'numeric.wave_gauge_positions')}
        </section>
      </div>
    `;
    
    if (editable) {
      attachEventListeners();
    }
  };
  
  const handleFieldChange = debounce((path, value, isArray = false) => {
    if (isArray) {
      // Parse comma-separated values
      value = value.split(',').map(v => parseFloat(v.trim())).filter(v => !isNaN(v));
    }
    configStore.updateConfig(path, value);
  }, 300);
  
  const attachEventListeners = () => {
    // Text and number inputs
    container.querySelectorAll('input[type="text"], input[type="number"]').forEach(input => {
      input.addEventListener('input', (e) => {
        const path = e.target.dataset.path;
        const value = e.target.value;
        const isArray = e.target.dataset.array === 'true';
        handleFieldChange(path, value, isArray);
      });
    });
    
    // Checkboxes
    container.querySelectorAll('input[type="checkbox"]').forEach(input => {
      input.addEventListener('change', (e) => {
        const path = e.target.dataset.path;
        const value = e.target.checked;
        configStore.updateConfig(path, value);
      });
    });
  };
  
  const mount = () => {
    unsubscribe = configStore.subscribe(render);
  };
  
  const unmount = () => {
    if (unsubscribe) {
      unsubscribe();
      unsubscribe = null;
    }
  };
  
  return { mount, unmount };
}