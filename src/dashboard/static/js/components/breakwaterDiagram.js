// Channel diagram component

import { svg } from '../utils.js';

export function createChannelDiagram(container, configStore) {
  let unsubscribe = null;
  
  const render = (config) => {
    if (!config) return;
    
    // Validate required numeric values before proceeding
    const requiredValues = [
      config.water?.water_level,
      config.water?.wave_height,
      config.water?.wave_period
    ];
    
    if (requiredValues.some(val => val === undefined || val === null || val === '' || isNaN(val))) {
      container.innerHTML = '<p style="color: var(--subtext0); padding: 20px;">Complete the configuration to see the diagram</p>';
      return;
    }
    
    // SVG dimensions and margins
    const margin = { top: 20, right: 20, bottom: 40, left: 40 };
    const height = 360;
    const plotHeight = height - margin.top - margin.bottom;
    
    // Get the actual available width (accounting for panel padding)
    const containerWidth = container.offsetWidth - 48; // Subtract panel padding (24px * 2)
    
    // Create SVG container with horizontal scrolling
    const svgContainer = document.createElement('div');
    svgContainer.style.width = `${containerWidth}px`;
    svgContainer.style.height = '400px';
    svgContainer.style.backgroundColor = 'var(--mantle)';
    svgContainer.style.borderRadius = '8px';
    svgContainer.style.padding = '20px';
    svgContainer.style.overflowX = 'auto';
    svgContainer.style.overflowY = 'hidden';
    svgContainer.style.position = 'relative';
    svgContainer.style.boxSizing = 'border-box';
    
    // Calculate channel dimensions (112m from template)
    const channelLength = 112.0;
    
    // Calculate full domain bounds for scrolling
    const fullDiagramStart = 0;
    const fullDiagramEnd = channelLength;
    const fullDiagramLength = fullDiagramEnd - fullDiagramStart;
    
    // Calculate visible bounds: show full channel initially
    const visibleStart = 0;
    const visibleEnd = channelLength;
    const visibleLength = visibleEnd - visibleStart;
    
    // Use same scale for both axes to maintain correct proportions
    // Ensure at least 3m vertical display
    const maxHeight = Math.max(3.0, config.water.water_level + 1); // At least 3m or water level + 1m margin
    const availableWidth = containerWidth - margin.left - margin.right;
    
    // Calculate scale - use full vertical space, same scale for horizontal
    const yScale = plotHeight / maxHeight;
    const scale = yScale; // Use vertical scale for both directions
    
    // Calculate dimensions
    const actualPlotHeight = plotHeight; // Use full vertical space
    const fullPlotWidth = fullDiagramLength * scale; // Full scrollable width (will be wider)
    
    // Use full plot height (no vertical centering)
    const yOffset = 0;
    
    // SVG dimensions: full width for scrolling, fixed height
    const svgWidth = fullPlotWidth + margin.left + margin.right;
    const svgHeight = height;
    
    // Create SVG
    const svgEl = svg('svg', {
      width: svgWidth,
      height: svgHeight,
      viewBox: `0 0 ${svgWidth} ${svgHeight}`,
      style: 'display: block;'
    });
    
    // Background
    svgEl.appendChild(svg('rect', {
      x: 0,
      y: 0,
      width: svgWidth,
      height: svgHeight,
      fill: 'var(--mantle)'
    }));
    
    // Create main group with margins and vertical centering
    const g = svg('g', {
      transform: `translate(${margin.left},${margin.top + yOffset})`
    });
    
    // Sea floor
    g.appendChild(svg('line', {
      x1: 0,
      y1: actualPlotHeight,
      x2: fullPlotWidth,
      y2: actualPlotHeight,
      stroke: 'var(--surface2)',
      'stroke-width': 2
    }));
    
    // Water level (as reference line)
    const waterY = actualPlotHeight - (config.water.water_level * scale);
    g.appendChild(svg('line', {
      x1: 0,
      y1: waterY,
      x2: fullPlotWidth,
      y2: waterY,
      stroke: 'var(--blue)',
      'stroke-width': 1,
      'stroke-dasharray': '3,3',
      opacity: 0.5
    }));
    
    // Add sinusoidal waves
    const wavelength = config.water.wavelength; // Get from API
    if (wavelength && !isNaN(wavelength) && wavelength > 0) {
      const waveAmplitude = (config.water.wave_height / 2) * scale;
      const wavelengthScaled = wavelength * scale;
      
      // Create wave path
      const wavePoints = [];
      const numWavePoints = Math.ceil(fullPlotWidth / 2); // Point every 2 pixels
      
      for (let i = 0; i <= numWavePoints; i++) {
        const x = (i * 2);
        const realX = x / scale + fullDiagramStart; // Convert back to real coordinates
        const wavePhase = (2 * Math.PI * realX) / wavelength;
        const waveElevation = waveAmplitude * Math.sin(wavePhase);
        const y = waterY - waveElevation;
        wavePoints.push(`${i === 0 ? 'M' : 'L'} ${x} ${y}`);
      }
      
      g.appendChild(svg('path', {
        d: wavePoints.join(' '),
        stroke: 'var(--blue)',
        'stroke-width': 2,
        fill: 'none'
      }));
    }
    
    // Simple channel - just show the flat bottom
    
    // Channel length label (below distance labels)
    g.appendChild(svg('text', {
      x: fullPlotWidth / 2,
      y: actualPlotHeight + 35,
      'text-anchor': 'middle',
      fill: 'var(--text)',
      'font-size': '14'
    }, [`Channel Length: ${channelLength}m`]));
    
    // Wave parameters label
    if (wavelength && !isNaN(wavelength) && wavelength > 0) {
      const waveAmplitude = (config.water.wave_height / 2) * scale;
      g.appendChild(svg('text', {
        x: 10,
        y: waterY - waveAmplitude - 15,
        'text-anchor': 'start',
        fill: 'var(--blue)',
        'font-size': '11'
      }, [`H=${config.water.wave_height}m, T=${config.water.wave_period}s, λ=${wavelength.toFixed(1)}m`]));
    }
    
    // Wave gauges (if configured)
    if (config.numeric?.wave_gauge_positions) {
      config.numeric.wave_gauge_positions.forEach((pos, i) => {
        // Only show gauges within the diagram bounds
        if (pos < fullDiagramStart || pos > fullDiagramEnd) return;
        const x = (pos - fullDiagramStart) * scale;
        g.appendChild(svg('line', {
          x1: x,
          y1: waterY - 10,
          x2: x,
          y2: actualPlotHeight,
          stroke: 'var(--yellow)',
          'stroke-width': 1,
          'stroke-dasharray': '2,2'
        }));
        g.appendChild(svg('text', {
          x: x,
          y: waterY - 15,
          'text-anchor': 'middle',
          fill: 'var(--yellow)',
          'font-size': '10'
        }, [`G${i + 1}`]));
      });
    }
    
    // X-axis labels - use appropriate interval based on diagram length
    const labelInterval = fullDiagramLength > 100 ? 20 : fullDiagramLength > 50 ? 10 : 5;
    const labelStart = Math.ceil(fullDiagramStart / labelInterval) * labelInterval;
    for (let x = labelStart; x <= fullDiagramEnd; x += labelInterval) {
      const xPos = (x - fullDiagramStart) * scale;
      g.appendChild(svg('text', {
        x: xPos,
        y: actualPlotHeight + 20,
        'text-anchor': 'middle',
        fill: 'var(--subtext0)',
        'font-size': '12'
      }, [`${x}m`]));
    }
    
    svgEl.appendChild(g);
    
    // Create fixed overlay for WL label that doesn't scroll
    const overlayEl = svg('svg', {
      width: margin.left,
      height: height,
      style: 'position: absolute; left: 20px; top: 20px; pointer-events: none;'
    });
    
    const overlayG = svg('g', {
      transform: `translate(0, ${margin.top + yOffset})`
    });
    
    // Add fixed WL label
    overlayG.appendChild(svg('text', {
      x: margin.left - 10,
      y: waterY,
      'text-anchor': 'end',
      'dominant-baseline': 'middle',
      fill: 'var(--blue)',
      'font-size': '12'
    }, ['WL']));
    
    overlayEl.appendChild(overlayG);
    
    svgContainer.appendChild(svgEl);
    svgContainer.appendChild(overlayEl);
    container.appendChild(svgContainer);
    
    // Set initial scroll position centered on the channel after DOM update
    requestAnimationFrame(() => {
      const channelCenter = channelLength / 2;
      const channelCenterInSvg = (channelCenter - fullDiagramStart) * scale + margin.left;
      const viewportCenter = svgContainer.clientWidth / 2;
      const centerScrollOffset = channelCenterInSvg - viewportCenter;
      svgContainer.scrollLeft = Math.max(0, centerScrollOffset);
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
