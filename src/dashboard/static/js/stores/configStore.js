// Config store for managing shared configuration state

import * as api from '../api.js';

export function createConfigStore() {
  let config = null;
  const subscribers = new Set();
  
  return {
    subscribe: (callback) => {
      subscribers.add(callback);
      // Immediately notify with current state
      if (config) callback(config);
      // Return unsubscribe function
      return () => subscribers.delete(callback);
    },
    
    getConfig: () => config,
    
    setConfig: (newConfig) => {
      config = newConfig;
      // Notify all subscribers
      subscribers.forEach(cb => cb(config));
    },
    
    updateConfig: async (path, value) => {
      if (!config) return;
      
      // Deep clone and update
      const updated = JSON.parse(JSON.stringify(config));
      const keys = path.split('.');
      let current = updated;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      
      const finalKey = keys[keys.length - 1];
      
      // Handle parsing similar to the example project
      if (typeof value === 'string' && value !== '') {
        const numericValue = parseFloat(value.replace(',', '.'));
        current[finalKey] = !isNaN(numericValue) ? numericValue : value;
      } else {
        current[finalKey] = value;
      }
      
      // If water parameters changed, recalculate wavelength
      if (path.startsWith('water.') && (path.includes('wave_period') || path.includes('water_level'))) {
        try {
          // Only recalculate if we have valid values
          const wavePeriod = updated.water.wave_period;
          const waterLevel = updated.water.water_level;
          
          if (typeof wavePeriod === 'number' && wavePeriod > 0 && 
              typeof waterLevel === 'number' && waterLevel > 0) {
            const response = await fetch('/api/wavelength', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                wave_period: wavePeriod,
                water_level: waterLevel
              })
            });
            
            if (response.ok) {
              const data = await response.json();
              updated.water.wavelength = data.wavelength;
            }
          }
        } catch (error) {
          // Silently ignore wavelength calculation errors
        }
      }
      
      config = updated;
      subscribers.forEach(cb => cb(config));
    }
  };
}