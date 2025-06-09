// Config detail view

import * as api from '../api.js';
import { createConfigStore } from '../stores/configStore.js';
import { createConfigViewer } from '../components/configViewer.js';
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
      const analysis = await api.getAnalysis(configName);
      renderAnalysisResults(analysis);
    } catch (error) {
      console.error('Error loading analysis:', error);
      document.getElementById('analysis').innerHTML = `
        <h3>Analysis Results</h3>
        <p style="color: var(--red); text-align: center; padding: 40px;">
          Error loading analysis: ${error.message}
        </p>
      `;
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
        <div class="analysis-metrics">
          <h4>Wave Attenuation</h4>
          <div class="metric-cards">
            <div class="metric-card">
              <span class="metric-label">Transmission Coefficient (Kt)</span>
              <span class="metric-value">${analysis.transmission_analysis.transmission_coefficient?.toFixed(3) || 'N/A'}</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Energy Dissipation</span>
              <span class="metric-value">${analysis.transmission_analysis.energy_dissipation_percent?.toFixed(1) || 'N/A'}%</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Incident Wave Height</span>
              <span class="metric-value">${analysis.transmission_analysis.incident_wave_height?.toFixed(3) || 'N/A'} m</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Transmitted Wave Height</span>
              <span class="metric-value">${analysis.transmission_analysis.transmitted_wave_height?.toFixed(3) || 'N/A'} m</span>
            </div>
          </div>
        </div>
        <div class="analysis-plot">
          <h4>Wave Gauge Time Series</h4>
          <div id="time-series-plot" style="width: 100%; height: 500px;"></div>
        </div>
      </div>
    `;

    // Render the plotly chart with Catppuccin theme
    if (analysis.time_series_plot && window.Plotly) {
      const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        toImageButtonOptions: {
          format: 'png',
          filename: 'wave_analysis',
          height: 500,
          width: 1000,
          scale: 2
        }
      };

      // Apply additional Catppuccin theming to layout
      const layout = {
        ...analysis.time_series_plot.layout,
        modebar: {
          bgcolor: 'rgba(49, 50, 68, 0.8)',
          color: '#cdd6f4',
          activecolor: '#89b4fa'
        }
      };

      window.Plotly.newPlot('time-series-plot', analysis.time_series_plot.data, layout, config);
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
