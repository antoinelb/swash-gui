// Config store for managing shared configuration state

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
    
    updateConfig: (path, value) => {
      if (!config) return;
      
      // Deep clone and update
      const updated = JSON.parse(JSON.stringify(config));
      const keys = path.split('.');
      let current = updated;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      
      const finalKey = keys[keys.length - 1];
      current[finalKey] = typeof value === 'string' && !isNaN(value) 
        ? parseFloat(value) 
        : value;
      
      config = updated;
      subscribers.forEach(cb => cb(config));
    }
  };
}