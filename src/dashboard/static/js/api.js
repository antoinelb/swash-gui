// API client for dashboard

const API_BASE = '/api';

// Helper for API calls
async function apiCall(url, options = {}) {
  try {
    const response = await fetch(API_BASE + url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Config API
export async function listConfigs() {
  const data = await apiCall('/configs');
  return data.configs;
}

export async function getConfig(name) {
  return await apiCall(`/configs/${name}`);
}

export async function createConfig(config) {
  return await apiCall('/configs', {
    method: 'POST',
    body: JSON.stringify(config),
  });
}

export async function updateConfig(name, config) {
  return await apiCall(`/configs/${name}`, {
    method: 'PUT',
    body: JSON.stringify(config),
  });
}

export async function deleteConfig(name) {
  return await apiCall(`/configs/${name}`, {
    method: 'DELETE',
  });
}

export async function runSimulation(name) {
  return await apiCall(`/simulate/${name}`, {
    method: 'POST',
  });
}
