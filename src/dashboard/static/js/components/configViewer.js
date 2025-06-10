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

  const createSelectField = (label, value, path, options) => {
    const fieldId = path.replace(/\./g, '-');

    if (editable) {
      const optionElements = options.map(opt => 
        `<option value="${opt.value}" ${value === opt.value ? 'selected' : ''}>${opt.label}</option>`
      ).join('');
      
      return `
<div class="field">
  <label for="${fieldId}">${label}</label>
  <select id="${fieldId}" data-path="${path}">
    ${optionElements}
  </select>
</div>
`;
    } else {
      const selectedOption = options.find(opt => opt.value === value);
      return `
<div class="field">
  <label>${label}</label>
  <span class="field-value">${selectedOption ? selectedOption.label : value}</span>
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
    <h3>Breakwater</h3>
    ${createCheckbox('Enable Breakwater', config.breakwater.enable, 'breakwater.enable')}
    ${config.breakwater.enable || editable ? `
    ${createField('Crest Height (m)', config.breakwater.crest_height, 'breakwater.crest_height')}
    ${createField('Crest Width (m)', config.breakwater.crest_width, 'breakwater.crest_width')}
    ${createField('Slope (H:V)', config.breakwater.slope, 'breakwater.slope')}
    ${createField('Porosity', config.breakwater.porosity, 'breakwater.porosity')}
    ${createField('Stone Density (kg/m³)', config.breakwater.stone_density, 'breakwater.stone_density')}
    ${createField('Armour Dn50 (m)', config.breakwater.armour_dn50, 'breakwater.armour_dn50')}
    ${createField('Start Position (m)', config.breakwater.breakwater_start_position, 'breakwater.breakwater_start_position')}
    ` : ''}
  </section>

  <section>
    <h3>Vegetation</h3>
    ${createCheckbox('Enable Vegetation', config.vegetation.enable, 'vegetation.enable')}
    
    ${config.vegetation.enable || editable ? `
    <h4>Primary Type</h4>
    ${createField('Plant Height (m)', config.vegetation.type?.plant_height || 0, 'vegetation.type.plant_height')}
    ${createField('Plant Diameter (m)', config.vegetation.type?.plant_diameter || 0, 'vegetation.type.plant_diameter')}
    ${createField('Plant Density (/m²)', config.vegetation.type?.plant_density || 0, 'vegetation.type.plant_density')}
    ${createField('Drag Coefficient', config.vegetation.type?.drag_coefficient || 0, 'vegetation.type.drag_coefficient')}
    
    ${config.vegetation.other_type ? `
    ${editable ? `<div class="vegetation-controls">
      <button type="button" class="btn btn-danger btn-sm" data-action="remove-vegetation-type">Remove Secondary Type</button>
    </div>` : ''}
    <h4>Secondary Type</h4>
    ${createField('Plant Height (m)', config.vegetation.other_type.plant_height, 'vegetation.other_type.plant_height')}
    ${createField('Plant Diameter (m)', config.vegetation.other_type.plant_diameter, 'vegetation.other_type.plant_diameter')}
    ${createField('Plant Density (/m²)', config.vegetation.other_type.plant_density, 'vegetation.other_type.plant_density')}
    ${createField('Drag Coefficient', config.vegetation.other_type.drag_coefficient, 'vegetation.other_type.drag_coefficient')}
    
    <h4>Distribution</h4>
    ${createSelectField('Distribution Pattern', config.vegetation.distribution, 'vegetation.distribution', [
      { value: 'half', label: 'Half (Seaward/Leeward)' },
      { value: 'alternating', label: 'Alternating Pattern' },
      { value: 'custom', label: 'Custom Proportion' }
    ])}
    ${createField('Primary Type Fraction', config.vegetation.type_fraction, 'vegetation.type_fraction')}
    ` : editable ? `
    <div class="vegetation-controls">
      <button type="button" class="btn btn-primary btn-sm" data-action="add-vegetation-type">Add Secondary Type</button>
    </div>
    ` : ''}
    ` : ''}
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

    updateField('breakwater.enable', config.breakwater.enable);
    updateField('breakwater.crest_height', config.breakwater.crest_height);
    updateField('breakwater.crest_width', config.breakwater.crest_width);
    updateField('breakwater.slope', config.breakwater.slope);
    updateField('breakwater.porosity', config.breakwater.porosity);
    updateField('breakwater.stone_density', config.breakwater.stone_density);
    updateField('breakwater.armour_dn50', config.breakwater.armour_dn50);
    updateField('breakwater.breakwater_start_position', config.breakwater.breakwater_start_position);

    updateField('vegetation.enable', config.vegetation.enable);
    
    // Primary vegetation type
    updateField('vegetation.type.plant_height', config.vegetation.type?.plant_height);
    updateField('vegetation.type.plant_diameter', config.vegetation.type?.plant_diameter);
    updateField('vegetation.type.plant_density', config.vegetation.type?.plant_density);
    updateField('vegetation.type.drag_coefficient', config.vegetation.type?.drag_coefficient);
    
    // Secondary vegetation type
    if (config.vegetation.other_type) {
      updateField('vegetation.other_type.plant_height', config.vegetation.other_type.plant_height);
      updateField('vegetation.other_type.plant_diameter', config.vegetation.other_type.plant_diameter);
      updateField('vegetation.other_type.plant_density', config.vegetation.other_type.plant_density);
      updateField('vegetation.other_type.drag_coefficient', config.vegetation.other_type.drag_coefficient);
      updateField('vegetation.distribution', config.vegetation.distribution);
      updateField('vegetation.type_fraction', config.vegetation.type_fraction);
    }

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

    // Select dropdowns
    container.querySelectorAll('select').forEach(select => {
      select.addEventListener('change', (e) => {
        const path = e.target.dataset.path;
        const value = e.target.value;
        configStore.updateConfig(path, value);
      });
    });

    // Vegetation control buttons
    container.querySelectorAll('[data-action]').forEach(button => {
      button.addEventListener('click', (e) => {
        const action = e.target.dataset.action;
        
        if (action === 'add-vegetation-type') {
          // Add a default secondary vegetation type
          const defaultSecondaryType = {
            plant_height: 0.3,
            plant_diameter: 0.015,
            plant_density: 50.0,
            drag_coefficient: 1.0
          };
          configStore.updateConfig('vegetation.other_type', defaultSecondaryType);
          configStore.updateConfig('vegetation.distribution', 'half');
          configStore.updateConfig('vegetation.type_fraction', 0.5);
          // Re-render to show new fields
          isInitialized = false;
          render(configStore.getConfig());
        } else if (action === 'remove-vegetation-type') {
          // Remove secondary vegetation type
          configStore.updateConfig('vegetation.other_type', null);
          // Re-render to hide secondary type fields
          isInitialized = false;
          render(configStore.getConfig());
        }
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
