// Config create view

import * as api from '../api.js';
import { createConfigStore } from '../stores/configStore.js';
import { createConfigViewer } from '../components/configViewer.js';
import { icon } from '../utils.js';

export function createConfigCreateView() {
  const container = document.getElementById('app');
  const configStore = createConfigStore();
  let components = [];
  
  // Default config template
  const defaultConfig = {
    name: 'new-config',
    grid: {
      length: 100.0,
      nx_cells: 1000,
      n_layers: 10
    },
    breakwater: {
      crest_height: 2.0,
      crest_width: 5.0,
      slope: 2.0,
      porosity: 0.4,
      stone_density: 2650.0,
      armour_dn50: 0.3,
      filter_dn50: 0.1,
      core_dn50: 0.05
    },
    water: {
      water_level: 5.0,
      water_density: 1025.0,
      wave_height: 2.0,
      wave_period: 8.0
    },
    vegetation: {
      enable: false,
      plant_height: 0.5,
      plant_diameter: 0.01,
      plant_density: 100.0,
      drag_coefficient: 1.0
    },
    numeric: {
      n_waves: 10,
      time_step: 0.01,
      breakwater_start_position: 40.0,
      output_interval: 1.0,
      wave_gauge_positions: [20.0, 30.0, 70.0, 80.0]
    }
  };
  
  const render = () => {
    container.innerHTML = `
      <div class="header">
        <h1>${icon('plus-circle')} Create New Configuration</h1>
        <div class="actions">
          <button class="btn btn-secondary" onclick="router.push('/configs')">
            ${icon('x')} Cancel
          </button>
          <button class="btn btn-success" id="save-btn">
            ${icon('save')} Save Configuration
          </button>
        </div>
      </div>
      
      <div class="panel" style="margin-bottom: 24px;">
        <h3>Copy from existing configuration</h3>
        <select id="copy-select" class="field-input" style="width: 300px;">
          <option value="">Start from scratch</option>
        </select>
        <button class="btn btn-secondary" id="copy-btn" style="margin-left: 8px;">
          ${icon('copy')} Copy
        </button>
      </div>
      
      <div id="config-viewer" class="panel"></div>
    `;
    
    // Attach event listeners
    document.getElementById('save-btn')?.addEventListener('click', saveConfig);
    document.getElementById('copy-btn')?.addEventListener('click', copyFromExisting);
  };
  
  const loadExistingConfigs = async () => {
    try {
      const configs = await api.listConfigs();
      const select = document.getElementById('copy-select');
      
      configs.forEach(cfg => {
        const option = document.createElement('option');
        option.value = cfg.name;
        option.textContent = `Copy from ${cfg.name}`;
        select.appendChild(option);
      });
    } catch (error) {
      console.error('Error loading configs:', error);
    }
  };
  
  const copyFromExisting = async () => {
    const select = document.getElementById('copy-select');
    const selectedName = select.value;
    
    if (!selectedName) {
      configStore.setConfig(defaultConfig);
      return;
    }
    
    try {
      const config = await api.getConfig(selectedName);
      // Reset name for new config
      config.name = 'new-config';
      configStore.setConfig(config);
    } catch (error) {
      alert(`Error loading configuration: ${error.message}`);
    }
  };
  
  const saveConfig = async () => {
    try {
      const config = configStore.getConfig();
      
      // Validate name
      if (!config.name || config.name.trim() === '') {
        alert('Please enter a configuration name');
        return;
      }
      
      await api.createConfig(config);
      alert('Configuration created successfully!');
      router.push(`/config/${config.name}`);
    } catch (error) {
      alert(`Error creating configuration: ${error.message}`);
    }
  };
  
  const mount = async () => {
    // Render layout
    render();
    
    // Load existing configs for copy dropdown
    await loadExistingConfigs();
    
    // Set default config
    configStore.setConfig(defaultConfig);
    
    // Create and mount config viewer (editable)
    const viewer = createConfigViewer(
      document.getElementById('config-viewer'),
      configStore,
      true  // editable
    );
    viewer.mount();
    components.push(viewer);
    
    // Return cleanup function
    return () => {
      components.forEach(c => c.unmount());
    };
  };
  
  return { mount };
}