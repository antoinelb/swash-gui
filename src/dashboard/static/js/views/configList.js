// Config list view

import * as api from '../api.js';
import { icon } from '../utils.js';

export function createConfigListView() {
  const container = document.getElementById('app');
  let configs = [];
  
  const render = () => {
    const configCards = configs.map(cfg => `
      <a href="/config/${cfg.name}" class="config-card">
        <h3>${cfg.name}</h3>
        <div class="config-hash">Hash: ${cfg.hash}</div>
      </a>
    `).join('');
    
    container.innerHTML = `
      <div class="header">
        <h1>${icon('settings')} SWASH Configurations</h1>
        <div class="actions">
          <button class="btn btn-primary" onclick="router.push('/create')">
            ${icon('plus')} New Configuration
          </button>
          <button class="btn btn-secondary" id="refresh-btn">
            ${icon('refresh-cw')} Refresh
          </button>
        </div>
      </div>
      
      ${configs.length > 0 ? `
        <div class="config-grid">
          ${configCards}
        </div>
      ` : `
        <div class="empty-state">
          <p>No configurations found.</p>
          <button class="btn btn-primary" onclick="router.push('/create')">
            ${icon('plus')} Create Your First Configuration
          </button>
        </div>
      `}
    `;
    
    // Attach event listeners
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', loadConfigs);
    }
  };
  
  const loadConfigs = async () => {
    try {
      configs = await api.listConfigs();
      render();
    } catch (error) {
      container.innerHTML = `
        <div class="error-message">
          <h2>Error Loading Configurations</h2>
          <p>${error.message}</p>
          <button class="btn" onclick="location.reload()">Reload Page</button>
        </div>
      `;
    }
  };
  
  const mount = async () => {
    await loadConfigs();
    // No cleanup needed for this view
    return () => {};
  };
  
  return { mount };
}