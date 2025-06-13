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
  <div id="diagram" class="panel">
    <div id="diagram-content"></div>
  </div>
  <div id="analysis" class="panel">
    <h3>Analysis Results</h3>
    <p style="color: var(--subtext0); text-align: center; padding: 40px;">
      Run simulation to see results
    </p>
  </div>
  <div id="config-viewer" class="panel"></div>
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

      // Load analysis results if simulation was successful
      if (result.success) {
        loadAnalysisResults();
      }

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

  const loadAnalysisResults = async () => {
    try {
      const analysis = await api.getAnalysisResults(configName);
      renderAnalysisResults(analysis);
    } catch (error) {
      renderAnalysisResults({ error: error.message });
    }
  };

  const renderAnalysisResults = (analysis) => {
    const analysisPanel = document.getElementById('analysis');

    if (analysis.error) {
      analysisPanel.innerHTML = `
<h3>Analysis Results</h3>
<p style="color: var(--red); text-align: center; padding: 40px;">
  ${analysis.error}
</p>
`;
      return;
    }

    analysisPanel.innerHTML = `
<h3>Analysis Results</h3>
<div class="analysis-content">
  <div class="analysis-plot">
    <div id="wave-envelope-plot" style="width: 100%; height: 500px;"></div>
  </div>
  ${analysis.wave_stats ? `
  <div class="wave-statistics">
    <h4>Wave Statistics by Gauge</h4>
    <table class="stats-table">
      <thead>
        <tr>
          <th>Position (m)</th>
          <th>Significant Wave Height (m)</th>
          <th>Mean Wave Height (m)</th>
          <th>Max Wave Height (m)</th>
          <th>Number of Waves</th>
          <th>Mean Period (s)</th>
        </tr>
      </thead>
      <tbody>
        ${analysis.wave_stats.map(stat => `
          <tr>
            <td>${stat.position.toFixed(1)}</td>
            <td>${stat.significant_wave_height.toFixed(3)}</td>
            <td>${stat.mean_wave_height.toFixed(3)}</td>
            <td>${stat.max_wave_height.toFixed(3)}</td>
            <td>${stat.n_waves}</td>
            <td>${stat.mean_period.toFixed(2)}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  </div>
  ` : ''}
</div>
`;

    // Render the plotly chart with Catppuccin theme
    if (analysis.plot_data && window.Plotly) {
      const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        toImageButtonOptions: {
          format: 'png',
          filename: 'wave_time_series',
          height: 500,
          width: 1000,
          scale: 2
        }
      };

      // Apply additional Catppuccin theming to layout
      const layout = {
        ...analysis.plot_data.layout,
        modebar: {
          bgcolor: 'rgba(49, 50, 68, 0.8)',
          color: '#cdd6f4',
          activecolor: '#89b4fa'
        }
      };

      window.Plotly.newPlot('wave-envelope-plot', analysis.plot_data.data, layout, config);
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
        document.getElementById('diagram-content'),
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

      // Try to load analysis results if they exist
      loadAnalysisResults();

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
