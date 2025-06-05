// Breakwater diagram component

import { svg } from '../utils.js';

export function createBreakwaterDiagram(container, configStore) {
  let unsubscribe = null;
  
  const render = (config) => {
    if (!config) return;
    
    // Validate required numeric values before proceeding
    const requiredValues = [
      config.numeric?.breakwater_start_position,
      config.breakwater?.crest_height,
      config.breakwater?.crest_width,
      config.breakwater?.slope,
      config.water?.water_level,
      config.water?.wave_height,
      config.water?.wave_period
    ];
    
    if (requiredValues.some(val => val === undefined || val === null || val === '' || isNaN(val))) {
      container.innerHTML = '<h3>Breakwater Cross-Section</h3><p style="color: var(--subtext0); padding: 20px;">Complete the configuration to see the diagram</p>';
      return;
    }
    
    container.innerHTML = '<h3>Breakwater Cross-Section</h3>';
    
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
    
    // Calculate breakwater dimensions
    const breakwaterStart = config.numeric.breakwater_start_position;
    const breakwaterHeight = config.breakwater.crest_height;
    const breakwaterSlope = config.breakwater.slope;
    const creastWidth = config.breakwater.crest_width;
    
    // Bottom width = crest width + 2 * (height * slope)
    const baseWidth = creastWidth + 2 * (breakwaterHeight * breakwaterSlope);
    const breakwaterEnd = breakwaterStart + baseWidth;
    
    // Calculate full domain bounds for scrolling - start from 0m
    const fullDiagramStart = 0;
    const fullDiagramEnd = breakwaterEnd + 10;
    const fullDiagramLength = fullDiagramEnd - fullDiagramStart;
    
    // Calculate visible bounds: 5m on each side of breakwater
    const visibleStart = Math.max(0, breakwaterStart - 5);
    const visibleEnd = breakwaterEnd + 5;
    const visibleLength = visibleEnd - visibleStart;
    
    // Use same scale for both axes to maintain correct proportions
    const maxHeight = config.water.water_level + 5; // Add some margin above water
    const availableWidth = containerWidth - margin.left - margin.right;
    
    // Calculate scale to fit visible area in container
    const xScaleFromVisible = availableWidth / visibleLength;
    const yScaleFromHeight = plotHeight / maxHeight;
    const scale = Math.min(xScaleFromVisible, yScaleFromHeight);
    
    // Calculate dimensions
    const actualPlotHeight = maxHeight * scale;
    const fullPlotWidth = fullDiagramLength * scale; // Full scrollable width
    const visiblePlotWidth = visibleLength * scale;   // Visible area width
    
    // Center vertically if smaller than available space
    const yOffset = Math.max(0, (plotHeight - actualPlotHeight) / 2);
    
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
    
    // Water level label (will be added as overlay later)
    
    // Breakwater
    const bwStart = (breakwaterStart - fullDiagramStart) * scale;
    const bwEnd = (breakwaterEnd - fullDiagramStart) * scale;
    const bwWidth = bwEnd - bwStart;
    const bwHeight = config.breakwater.crest_height * scale;
    const bwY = actualPlotHeight - bwHeight;
    
    // Breakwater core (trapezoid)
    // Slope offset in screen coordinates
    const slopeOffset = (breakwaterHeight * breakwaterSlope) * scale;
    const crestWidthScaled = creastWidth * scale;
    
    // Calculate trapezoid points
    const crestStart = bwStart + slopeOffset;
    const crestEnd = crestStart + crestWidthScaled;
    
    const breakwaterPath = [
      `M ${bwStart} ${actualPlotHeight}`,  // Bottom left
      `L ${crestStart} ${bwY}`,            // Top left
      `L ${crestEnd} ${bwY}`,              // Top right  
      `L ${bwEnd} ${actualPlotHeight}`,    // Bottom right
      `Z`
    ].join(' ');
    
    g.appendChild(svg('path', {
      d: breakwaterPath,
      fill: 'var(--surface1)',
      stroke: 'var(--surface2)',
      'stroke-width': 2
    }));
    
    // Vegetation on top (if enabled)
    let topOfStructure = bwY; // Track the highest point for label positioning
    if (config.vegetation.enable) {
      const vegHeight = config.vegetation.plant_height * scale;
      const vegSpacing = 5; // pixels between plants
      const numPlants = Math.floor(crestWidthScaled / vegSpacing);
      
      for (let i = 0; i < numPlants; i++) {
        const x = crestStart + i * vegSpacing;
        g.appendChild(svg('line', {
          x1: x,
          y1: bwY,
          x2: x,
          y2: bwY - vegHeight,
          stroke: 'var(--green)',
          'stroke-width': 1.5
        }));
      }
      
      topOfStructure = bwY - vegHeight; // Vegetation extends above breakwater
    }
    
    // Labels
    g.appendChild(svg('text', {
      x: (bwStart + bwEnd) / 2,
      y: actualPlotHeight + 20,
      'text-anchor': 'middle',
      fill: 'var(--text)',
      'font-size': '14'
    }, [`Breakwater: ${breakwaterStart.toFixed(1)}m - ${breakwaterEnd.toFixed(1)}m`]));
    
    // Height dimensions - position above vegetation if present
    const heightLabelY = config.vegetation.enable ? topOfStructure - 15 : bwY - 10;
    g.appendChild(svg('text', {
      x: (bwStart + bwEnd) / 2,
      y: heightLabelY,
      'text-anchor': 'middle',
      fill: 'var(--subtext0)',
      'font-size': '12'
    }, [`Height: ${config.breakwater.crest_height}m`]));
    
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
    
    // Wave gauges
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
    
    // X-axis labels - use appropriate interval based on diagram length
    const labelInterval = fullDiagramLength > 100 ? 20 : fullDiagramLength > 50 ? 10 : 5;
    const labelStart = Math.ceil(fullDiagramStart / labelInterval) * labelInterval;
    for (let x = labelStart; x <= fullDiagramEnd; x += labelInterval) {
      const xPos = (x - fullDiagramStart) * scale;
      g.appendChild(svg('text', {
        x: xPos,
        y: actualPlotHeight + 35,
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
    
    // Set initial scroll position centered on the breakwater after DOM update
    requestAnimationFrame(() => {
      const breakwaterCenter = (breakwaterStart + breakwaterEnd) / 2;
      const breakwaterCenterInSvg = (breakwaterCenter - fullDiagramStart) * scale + margin.left;
      const viewportCenter = svgContainer.clientWidth / 2;
      const centerScrollOffset = breakwaterCenterInSvg - viewportCenter;
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