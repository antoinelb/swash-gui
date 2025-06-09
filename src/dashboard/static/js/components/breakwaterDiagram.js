// Breakwater diagram component

import { svg } from '../utils.js';

export function createBreakwaterDiagram(container, configStore) {
  let unsubscribe = null;
  
  const render = (config) => {
    if (!config) return;
    
    // Check if breakwater is enabled
    const breakwaterEnabled = config.breakwater?.enable !== false;
    
    // Validate required numeric values before proceeding
    const baseRequiredValues = [
      config.water?.water_level,
      config.water?.wave_height,
      config.water?.wave_period
    ];
    
    const breakwaterRequiredValues = breakwaterEnabled ? [
      config.numeric?.breakwater_start_position,
      config.breakwater?.crest_height,
      config.breakwater?.crest_width,
      config.breakwater?.slope
    ] : [];
    
    const requiredValues = [...baseRequiredValues, ...breakwaterRequiredValues];
    
    if (requiredValues.some(val => val === undefined || val === null || val === '' || isNaN(val))) {
      const diagramTitle = breakwaterEnabled ? 'Breakwater Cross-Section' : 'Wave Channel Cross-Section';
      container.innerHTML = `<h3>${diagramTitle}</h3><p style="color: var(--subtext0); padding: 20px;">Complete the configuration to see the diagram</p>`;
      return;
    }
    
    const diagramTitle = breakwaterEnabled ? 'Breakwater Cross-Section' : 'Wave Channel Cross-Section';
    container.innerHTML = `<h3>${diagramTitle}</h3>`;
    
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
    
    // Calculate domain dimensions
    let breakwaterStart, breakwaterHeight, breakwaterSlope, creastWidth, baseWidth, breakwaterEnd;
    let fullDiagramStart, fullDiagramEnd, visibleStart, visibleEnd;
    
    if (breakwaterEnabled) {
      // Calculate breakwater dimensions
      breakwaterStart = config.numeric.breakwater_start_position;
      breakwaterHeight = config.breakwater.crest_height;
      breakwaterSlope = config.breakwater.slope;
      creastWidth = config.breakwater.crest_width;
      
      // Bottom width = crest width + 2 * (height * slope)
      baseWidth = creastWidth + 2 * (breakwaterHeight * breakwaterSlope);
      breakwaterEnd = breakwaterStart + baseWidth;
      
      // Calculate full domain bounds for scrolling - start from 0m
      fullDiagramStart = 0;
      fullDiagramEnd = breakwaterEnd + 10;
      
      // Calculate visible bounds: 5m on each side of breakwater
      visibleStart = Math.max(0, breakwaterStart - 5);
      visibleEnd = breakwaterEnd + 5;
    } else {
      // No breakwater - show a reasonable domain for wave channel
      fullDiagramStart = 0;
      fullDiagramEnd = 50; // 50m domain for wave channel
      
      // Show central portion by default
      visibleStart = 0;
      visibleEnd = 50;
    }
    
    const fullDiagramLength = fullDiagramEnd - fullDiagramStart;
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
    
    // Breakwater (only if enabled)
    let topOfStructure = actualPlotHeight; // Track the highest point for label positioning
    if (breakwaterEnabled) {
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
      topOfStructure = bwY; // Track the highest point for label positioning
        if (config.vegetation.enable && config.breakwater.enable) {
          const vegSpacing = 5; // pixels between plants
          const numPlants = Math.floor(crestWidthScaled / vegSpacing);
          
          // Check if we have two vegetation types
          const hasSecondType = config.vegetation.other_type && 
                               config.vegetation.other_type.plant_height && 
                               config.vegetation.other_type.plant_diameter;
          
          if (hasSecondType) {
            // Two vegetation types
            const type1Height = config.vegetation.type.plant_height * scale;
            const type2Height = config.vegetation.other_type.plant_height * scale;
            const maxVegHeight = Math.max(type1Height, type2Height);
            
            // Determine distribution
            const distribution = config.vegetation.distribution || 'half';
            const typeFraction = config.vegetation.type_fraction || 0.5;
            
            for (let i = 0; i < numPlants; i++) {
              const x = crestStart + i * vegSpacing;
              let isType1 = true;
              
              // Determine which type based on distribution
              if (distribution === 'half') {
                isType1 = i < numPlants * typeFraction;
              } else if (distribution === 'alternating') {
                isType1 = i % 2 === 0;
              } else if (distribution === 'custom') {
                isType1 = Math.random() < typeFraction;
              }
              
              const vegHeight = isType1 ? type1Height : type2Height;
              const vegColor = isType1 ? '#40a02b' : '#179299'; // Darker green for type 1, teal for type 2
              const strokeWidth = isType1 ? 2 : 1; // Thicker for shrubs, thinner for grasses
              
              g.appendChild(svg('line', {
                x1: x,
                y1: bwY,
                x2: x,
                y2: bwY - vegHeight,
                stroke: vegColor,
                'stroke-width': strokeWidth
              }));
            }
            
            topOfStructure = bwY - maxVegHeight;
          } else {
            // Single vegetation type (backward compatibility)
            const vegHeight = config.vegetation.type?.plant_height 
                             ? config.vegetation.type.plant_height * scale 
                             : config.vegetation.plant_height * scale;
            
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
            
            topOfStructure = bwY - vegHeight;
          }
        }
        
        // Breakwater labels
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
      } // End of breakwater conditional
    
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
    
    // Vegetation legend (if two types and breakwater enabled)
    if (breakwaterEnabled && config.vegetation.enable && config.vegetation.other_type && 
        config.vegetation.other_type.plant_height && config.vegetation.other_type.plant_diameter) {
      const legendX = fullPlotWidth - 150;
      const legendY = 20;
      
      // Type 1 legend
      g.appendChild(svg('line', {
        x1: legendX,
        y1: legendY,
        x2: legendX + 15,
        y2: legendY,
        stroke: '#40a02b',
        'stroke-width': 2
      }));
      g.appendChild(svg('text', {
        x: legendX + 20,
        y: legendY,
        'dominant-baseline': 'middle',
        fill: 'var(--subtext0)',
        'font-size': '11'
      }, [`Type 1: ${config.vegetation.type.plant_density}/m²`]));
      
      // Type 2 legend
      g.appendChild(svg('line', {
        x1: legendX,
        y1: legendY + 20,
        x2: legendX + 15,
        y2: legendY + 20,
        stroke: '#179299',
        'stroke-width': 1
      }));
      g.appendChild(svg('text', {
        x: legendX + 20,
        y: legendY + 20,
        'dominant-baseline': 'middle',
        fill: 'var(--subtext0)',
        'font-size': '11'
      }, [`Type 2: ${config.vegetation.other_type.plant_density}/m²`]));
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