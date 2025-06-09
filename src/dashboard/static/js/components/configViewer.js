// Config viewer/editor component

export function createConfigViewer(container, configStore, editable = false) {
  let unsubscribe = null;

  const createField = (label, value, path, type = 'number') => {
    const fieldId = path.replace(/\./g, '-');

    if (editable) {
      return `
<div class="field">
  <label for="${fieldId}">${label}</label>
  <input type="${type}" id="${fieldId}" value="${value}" data-path="${path}" ${type === 'number' ? 'step="0.01"' : ''} />
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
  <input type="text" id="${fieldId}" value="${valueStr}" data-path="${path}" data-array="true"
    placeholder="Comma-separated values" />
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
  <input type="checkbox" id="${fieldId}" data-path="${path}" ${value ? 'checked' : ''} />
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

  let isInitialized = false;

  const render = (config) => {
    if (!config) return;

    if (!isInitialized) {
      // Only create the DOM structure once
      container.innerHTML = `
<h3>Configuration</h3>
<div class="config-form">
  <section>
    <h3>General</h3>
    ${createField('Name', config.name, 'name', 'text')}
    ${!editable ? createField('Hash', config.hash?.substring(0, 8) || 'N/A', 'hash', 'text') : ''}
  </section>



  <section>
    <h3>Water & Waves</h3>
    ${createField('Water Level (m)', config.water.water_level, 'water.water_level')}
    ${createField('Water Density (kg/m³)', config.water.water_density, 'water.water_density')}
    ${createField('Wave Height (m)', config.water.wave_height, 'water.wave_height')}
    ${createField('Wave Period (s)', config.water.wave_period, 'water.wave_period')}
  </section>


  <section>
    <h3>Numerical Parameters</h3>
    ${createField('Number of Waves', config.numeric.n_waves, 'numeric.n_waves')}
    ${createArrayField('Wave Gauge Positions (m)', config.numeric.wave_gauge_positions, 'numeric.wave_gauge_positions')}
  </section>
</div>
`;

      if (editable) {
        attachEventListeners();
      }
      isInitialized = true;
    } else {
      // Only update field values without recreating DOM
      updateFieldValues(config);
    }
  };

  const updateFieldValues = (config) => {
    // Update values without recreating the DOM structure
    const updateField = (path, value) => {
      const fieldId = path.replace(/\./g, '-');
      const input = container.querySelector(`#${fieldId}`);
      if (input && document.activeElement !== input) {
        // Only update if the field is not currently focused
        if (input.type === 'checkbox') {
          input.checked = !!value;
        } else {
          input.value = value || '';
        }
      }
    };

    // Update all field values
    updateField('name', config.name);
    if (!editable) updateField('hash', config.hash?.substring(0, 8) || 'N/A');

    // Grid parameters are fixed - no need to update


    updateField('water.water_level', config.water.water_level);
    updateField('water.water_density', config.water.water_density);
    updateField('water.wave_height', config.water.wave_height);
    updateField('water.wave_period', config.water.wave_period);


    updateField('numeric.n_waves', config.numeric.n_waves);
    // Time step and output interval are fixed - no need to update
    updateField('numeric.wave_gauge_positions', config.numeric.wave_gauge_positions?.join(', '));
  };

  const handleFieldChange = (path, value, isArray = false) => {
    if (isArray) {
      // Parse comma-separated values for arrays
      const values = value.split(',')
        .map(v => v.trim())
        .filter(v => v !== '')
        .map(v => parseFloat(v))
        .filter(v => !isNaN(v));

      configStore.updateConfig(path, values);
    } else {
      // Always pass the raw value to config store - let it handle parsing/validation
      configStore.updateConfig(path, value);
    }
  };

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
