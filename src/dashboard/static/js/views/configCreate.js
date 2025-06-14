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
      // Grid parameters are fixed at 112.0m length, 500 cells, 2 layers
    },
    water: {
      water_level: 1.0,
      water_density: 1000.0,
      wave_height: 0.5,
      wave_period: 6.0
    },
    breakwater: {
      enable: false,
      crest_height: 1.5,
      crest_length: 3.0,
      slope: 2.0,
      porosity: 0.4,
      stone_density: 2650.0,
      armour_dn50: 0.5,
      breakwater_start_position: 70.0
    },
    vegetation: {
      enable: false,
      type: {
        plant_height: 0.5,
        plant_diameter: 0.01,
        plant_density: 100.0,
        drag_coefficient: 1.0
      },
      other_type: null,
      distribution: 'half',
      type_fraction: 0.5
    },
    numeric: {
      n_waves: 50,
      // Time step (0.05s) and output interval (0.1s) are fixed
      wave_gauge_positions: [20.0, 60.0, 80.0, 100.0]
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