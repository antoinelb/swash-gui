// Config detail view

import * as api from '../api.js';
import { createConfigStore } from '../stores/configStore.js';
import { createConfigViewer } from '../components/configViewer.js';
import { createBreakwaterDiagram } from '../components/breakwaterDiagram.js';
import { icon } from '../utils.js';

export function createConfigDetailView(configName) {
  const container = document.getElementById('app');
  const configStore = createConfigStore();
  let components = [];
  let isEditing = false;

  const render = () => {
    container.innerHTML = `
<div class="header">
  <h1>${icon('file-text')} ${configName}</h1>
  <div class="actions">
    <button class="btn btn-secondary" onclick="router.push('/configs')">
      ${icon('arrow-left')} Back
    </button>
    <button class="btn btn-secondary" id="edit-btn">
      ${icon('edit')} ${isEditing ? 'Cancel Edit' : 'Edit'}
    </button>
    ${isEditing ? `
    <button class="btn btn-success" id="save-btn">
      ${icon('save')} Save Changes
    </button>
    ` : `
    <button class="btn btn-primary" id="run-btn">
      ${icon('play')} Run Simulation
    </button>
    <button class="btn btn-danger" id="delete-btn">
      ${icon('trash-2')} Delete
    </button>
    `}
  </div>
</div>

<div class="config-detail">
  <div id="diagram" class="panel"></div>
  <div id="config-viewer" class="panel"></div>
  <div id="animation" class="panel">
    <h3>Wave Animation</h3>
    <p style="color: var(--subtext0); text-align: center; padding: 40px;">
      Animation will be displayed here
    </p>
  </div>
  <div id="analysis" class="panel">
    <h3>Analysis Results</h3>
    <p style="color: var(--subtext0); text-align: center; padding: 40px;">
      Run simulation to see results
    </p>
  </div>
</div>
`;

    // Attach event listeners
    document.getElementById('edit-btn')?.addEventListener('click', toggleEdit);
    document.getElementById('save-btn')?.addEventListener('click', saveConfig);
    document.getElementById('run-btn')?.addEventListener('click', runSimulation);
    document.getElementById('delete-btn')?.addEventListener('click', deleteConfig);
  };

  const toggleEdit = () => {
    isEditing = !isEditing;
    // Unmount components
    components.forEach(c => c.unmount());
    components = [];
    // Re-render and remount
    render();
    mountComponents();
  };

  const saveConfig = async () => {
    try {
      const config = configStore.getConfig();
      await api.updateConfig(configName, config);
      toggleEdit();
    } catch (error) {
      alert(`Error saving configuration: ${error.message}`);
    }
  };

  const runSimulation = async () => {
    try {
      const btn = document.getElementById('run-btn');
      btn.disabled = true;
      btn.innerHTML = `${icon('loader')} Running...`;

      const result = await api.runSimulation(configName);
      alert(result.message);

      btn.disabled = false;
      btn.innerHTML = `${icon('play')} Run Simulation`;
    } catch (error) {
      alert(`Error running simulation: ${error.message}`);
    }
  };

  const deleteConfig = async () => {
    if (!confirm(`Are you sure you want to delete "${configName}"?`)) return;

    try {
      await api.deleteConfig(configName);
      router.push('/configs');
    } catch (error) {
      alert(`Error deleting configuration: ${error.message}`);
    }
  };

  const mountComponents = () => {
    // Create and mount components
    components = [
      createConfigViewer(
        document.getElementById('config-viewer'),
        configStore,
        isEditing
      ),
      createBreakwaterDiagram(
        document.getElementById('diagram'),
        configStore
      ),
    ];

    components.forEach(c => c.mount());
  };

  const mount = async () => {
    try {
      // Render layout
      render();

      // Load config
      const config = await api.getConfig(configName);
      configStore.setConfig(config);

      // Mount components
      mountComponents();

      // Return cleanup function
      return () => {
        components.forEach(c => c.unmount());
      };
    } catch (error) {
      container.innerHTML = `
<div class="error-message">
  <h2>Error Loading Configuration</h2>
  <p>${error.message}</p>
  <button class="btn" onclick="router.push('/configs')">
    Back to List
  </button>
</div>
`;
      return () => { };
    }
  };

  return { mount };
}
