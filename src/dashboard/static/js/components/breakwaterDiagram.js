// Breakwater diagram component

import { svg, icon } from '../utils.js';

export function createBreakwaterDiagram(container, configStore) {
  let unsubscribe = null;
  let currentSvgEl = null;
  let currentConfig = null;
  
  const exportSVG = () => {
    if (!currentSvgEl) return;
    
    // Clone the SVG to avoid modifying the original
    const svgClone = currentSvgEl.cloneNode(true);
    
    // Get computed styles to resolve CSS variables
    const computedStyle = getComputedStyle(document.documentElement);
    const colorMap = {
      'var(--mantle)': computedStyle.getPropertyValue('--mantle').trim() || '#1e1e2e',
      'var(--surface2)': computedStyle.getPropertyValue('--surface2').trim() || '#585b70',
      'var(--surface1)': computedStyle.getPropertyValue('--surface1').trim() || '#45475a',
      'var(--blue)': computedStyle.getPropertyValue('--blue').trim() || '#89b4fa',
      'var(--green)': computedStyle.getPropertyValue('--green').trim() || '#a6e3a1',
      'var(--yellow)': computedStyle.getPropertyValue('--yellow').trim() || '#f9e2af',
      'var(--text)': computedStyle.getPropertyValue('--text').trim() || '#cdd6f4',
      'var(--subtext0)': computedStyle.getPropertyValue('--subtext0').trim() || '#a6adc8'
    };
    
    // Replace CSS variables with actual colors in the clone
    const replaceColors = (element) => {
      // Check attributes
      ['fill', 'stroke'].forEach(attr => {
        const value = element.getAttribute(attr);
        if (value && colorMap[value]) {
          element.setAttribute(attr, colorMap[value]);
        }
      });
      
      // Check style attribute
      const style = element.getAttribute('style');
      if (style) {
        let newStyle = style;
        Object.entries(colorMap).forEach(([varName, color]) => {
          newStyle = newStyle.replace(new RegExp(varName.replace(/[()]/g, '\\$&'), 'g'), color);
        });
        element.setAttribute('style', newStyle);
      }
      
      // Recurse through children
      Array.from(element.children).forEach(child => replaceColors(child));
    };
    
    replaceColors(svgClone);
    
    // Get SVG content
    const svgData = new XMLSerializer().serializeToString(svgClone);
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const svgUrl = URL.createObjectURL(svgBlob);
    
    // Create download link
    const downloadLink = document.createElement('a');
    downloadLink.href = svgUrl;
    downloadLink.download = `breakwater-diagram-${currentConfig?.name || 'export'}.svg`;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
    
    URL.revokeObjectURL(svgUrl);
  };
  
  const exportPNG = () => {
    if (!currentSvgEl) return;
    
    // Clone SVG to modify for export
    const svgClone = currentSvgEl.cloneNode(true);
    
    // Get computed styles to resolve CSS variables
    const computedStyle = getComputedStyle(document.documentElement);
    const colorMap = {
      'var(--mantle)': computedStyle.getPropertyValue('--mantle').trim() || '#1e1e2e',
      'var(--surface2)': computedStyle.getPropertyValue('--surface2').trim() || '#585b70',
      'var(--surface1)': computedStyle.getPropertyValue('--surface1').trim() || '#45475a',
      'var(--blue)': computedStyle.getPropertyValue('--blue').trim() || '#89b4fa',
      'var(--green)': computedStyle.getPropertyValue('--green').trim() || '#a6e3a1',
      'var(--yellow)': computedStyle.getPropertyValue('--yellow').trim() || '#f9e2af',
      'var(--text)': computedStyle.getPropertyValue('--text').trim() || '#cdd6f4',
      'var(--subtext0)': computedStyle.getPropertyValue('--subtext0').trim() || '#a6adc8'
    };
    
    // Replace CSS variables with actual colors in the clone
    const replaceColors = (element) => {
      // Check attributes
      ['fill', 'stroke'].forEach(attr => {
        const value = element.getAttribute(attr);
        if (value && colorMap[value]) {
          element.setAttribute(attr, colorMap[value]);
        }
      });
      
      // Check style attribute
      const style = element.getAttribute('style');
      if (style) {
        let newStyle = style;
        Object.entries(colorMap).forEach(([varName, color]) => {
          newStyle = newStyle.replace(new RegExp(varName.replace(/[()]/g, '\\$&'), 'g'), color);
        });
        element.setAttribute('style', newStyle);
      }
      
      // Recurse through children
      Array.from(element.children).forEach(child => replaceColors(child));
    };
    
    replaceColors(svgClone);
    
    // Get SVG dimensions
    const svgWidth = parseFloat(svgClone.getAttribute('width'));
    const svgHeight = parseFloat(svgClone.getAttribute('height'));
    
    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.width = svgWidth * 2; // 2x resolution for better quality
    canvas.height = svgHeight * 2;
    const ctx = canvas.getContext('2d');
    
    // Scale for high resolution
    ctx.scale(2, 2);
    
    // Convert SVG to data URL
    const svgData = new XMLSerializer().serializeToString(svgClone);
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);
    
    // Create image from SVG
    const img = new Image();
    img.onload = () => {
      // Draw image
      ctx.drawImage(img, 0, 0);
      
      // Export to PNG
      canvas.toBlob((blob) => {
        const pngUrl = URL.createObjectURL(blob);
        const downloadLink = document.createElement('a');
        downloadLink.href = pngUrl;
        downloadLink.download = `breakwater-diagram-${currentConfig?.name || 'export'}.png`;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        
        URL.revokeObjectURL(pngUrl);
        URL.revokeObjectURL(url);
      });
    };
    
    img.src = url;
  };
  
  const render = (config) => {
    if (!config) return;
    currentConfig = config;
    
    // Check if breakwater is enabled
    const breakwaterEnabled = config.breakwater?.enable !== false;
    
    // Validate required numeric values before proceeding
    const baseRequiredValues = [
      config.water?.water_level,
      config.water?.wave_height,
      config.water?.wave_period
    ];
    
    const breakwaterRequiredValues = breakwaterEnabled ? [
      config.breakwater?.breakwater_start_position,
      config.breakwater?.crest_height,
      config.breakwater?.crest_length,
      config.breakwater?.slope
    ] : [];
    
    const requiredValues = [...baseRequiredValues, ...breakwaterRequiredValues];
    
    if (requiredValues.some(val => val === undefined || val === null || val === '' || isNaN(val))) {
      const diagramTitle = breakwaterEnabled ? 'Breakwater Cross-Section' : 'Wave Channel Cross-Section';
      container.innerHTML = `<h3>${diagramTitle}</h3><p style="color: var(--subtext0); padding: 20px;">Complete the configuration to see the diagram</p>`;
      return;
    }
    
    const diagramTitle = breakwaterEnabled ? 'Breakwater Cross-Section' : 'Wave Channel Cross-Section';
    container.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <h3 style="margin: 0;">${diagramTitle}</h3>
        <div class="export-buttons" style="display: flex; gap: 8px;">
          <button class="btn btn-secondary btn-sm" id="export-svg-btn" title="Export as SVG">
            ${icon('download', 16)} SVG
          </button>
          <button class="btn btn-secondary btn-sm" id="export-png-btn" title="Export as PNG">
            ${icon('download', 16)} PNG
          </button>
        </div>
      </div>
    `;
    
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
    let breakwaterStart, breakwaterHeight, breakwaterSlope, crestWidth, baseWidth, breakwaterEnd;
    let fullDiagramStart, fullDiagramEnd, visibleStart, visibleEnd;
    
    if (breakwaterEnabled) {
      // Calculate breakwater dimensions
      breakwaterStart = config.breakwater.breakwater_start_position;
      breakwaterHeight = config.breakwater.crest_height;
      breakwaterSlope = config.breakwater.slope;
      crestWidth = config.breakwater.crest_length;
      
      // Bottom width = crest width + 2 * (height * slope)
      baseWidth = crestWidth + 2 * (breakwaterHeight * breakwaterSlope);
      breakwaterEnd = breakwaterStart + baseWidth;
      
      // Calculate full domain bounds for scrolling - start from 0m
      fullDiagramStart = 0;
      fullDiagramEnd = 112.0; // Full channel length
      
      // Calculate visible bounds: 5m on each side of breakwater
      visibleStart = Math.max(0, breakwaterStart - 5);
      visibleEnd = Math.min(112.0, breakwaterEnd + 5);
    } else {
      // No breakwater - show full channel
      fullDiagramStart = 0;
      fullDiagramEnd = 112.0;
      
      // Show full channel
      visibleStart = 0;
      visibleEnd = 112.0;
    }
    
    const fullDiagramLength = fullDiagramEnd - fullDiagramStart;
    const visibleLength = visibleEnd - visibleStart;
    
    // Use same scale for both axes to maintain correct proportions
    // Ensure the diagram shows at least the water level and structure with sufficient margin
    const vegetationHeight = config.vegetation?.enable ? 0.5 : 0; // meters, not pixels
    const structureTotalHeight = breakwaterEnabled ? (breakwaterHeight + vegetationHeight) : 0;
    const maxHeight = breakwaterEnabled ? Math.max(config.water.water_level + 2, structureTotalHeight + 1.5) : Math.max(3.0, config.water.water_level + 1);
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
      const crestWidthScaled = crestWidth * scale;
      
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
      
      topOfStructure = bwY; // Track the highest point for label positioning
      
      // Add vegetation if enabled
      if (config.vegetation?.enable) {
        const vegetationHeightMeters = 0.5; // Vegetation height in meters
        const vegetationHeightPixels = vegetationHeightMeters * scale; // Convert to pixels
        const vegetationY = bwY - vegetationHeightPixels;
        
        if (config.vegetation.other_type) {
          // Two vegetation types
          if (config.vegetation.distribution === 'half') {
            const crestMid = (crestStart + crestEnd) / 2;
            
            // Type 1 (seaward half)
            g.appendChild(svg('rect', {
              x: crestStart,
              y: vegetationY,
              width: crestMid - crestStart,
              height: vegetationHeightPixels,
              fill: 'var(--green)',
              opacity: 0.7
            }));
            
            // Type 2 (leeward half)
            g.appendChild(svg('rect', {
              x: crestMid,
              y: vegetationY,
              width: crestEnd - crestMid,
              height: vegetationHeightPixels,
              fill: 'var(--yellow)',
              opacity: 0.7
            }));
            
            // Vegetation type labels - position them above the vegetation with adequate spacing
            g.appendChild(svg('text', {
              x: (crestStart + crestMid) / 2,
              y: vegetationY - 8,
              'text-anchor': 'middle',
              fill: 'var(--green)',
              'font-size': '11'
            }, ['Type 1']));
            
            g.appendChild(svg('text', {
              x: (crestMid + crestEnd) / 2,
              y: vegetationY - 8,
              'text-anchor': 'middle',
              fill: 'var(--yellow)',
              'font-size': '11'
            }, ['Type 2']));
            
          } else {
            // For alternating and custom distributions, show as mixed pattern
            const patternWidth = 4;
            for (let x = crestStart; x < crestEnd; x += patternWidth * 2) {
              // Type 1 segments
              g.appendChild(svg('rect', {
                x: x,
                y: vegetationY,
                width: Math.min(patternWidth, crestEnd - x),
                height: vegetationHeightPixels,
                fill: 'var(--green)',
                opacity: 0.7
              }));
              
              // Type 2 segments
              if (x + patternWidth < crestEnd) {
                g.appendChild(svg('rect', {
                  x: x + patternWidth,
                  y: vegetationY,
                  width: Math.min(patternWidth, crestEnd - x - patternWidth),
                  height: vegetationHeightPixels,
                  fill: 'var(--yellow)',
                  opacity: 0.7
                }));
              }
            }
            
            // Single label for mixed vegetation - position above with adequate spacing
            g.appendChild(svg('text', {
              x: (crestStart + crestEnd) / 2,
              y: vegetationY - 8,
              'text-anchor': 'middle',
              fill: 'var(--green)',
              'font-size': '11'
            }, ['Mixed Vegetation']));
          }
        } else {
          // Single vegetation type
          g.appendChild(svg('rect', {
            x: crestStart,
            y: vegetationY,
            width: crestEnd - crestStart,
            height: vegetationHeight,
            fill: 'var(--green)',
            opacity: 0.7
          }));
          
          // Vegetation label - position above with adequate spacing
          g.appendChild(svg('text', {
            x: (crestStart + crestEnd) / 2,
            y: vegetationY - 8,
            'text-anchor': 'middle',
            fill: 'var(--green)',
            'font-size': '11'
          }, ['Vegetation']));
        }
        
        topOfStructure = vegetationY; // Update highest point
      }
        
      // Breakwater labels
      g.appendChild(svg('text', {
        x: (bwStart + bwEnd) / 2,
        y: actualPlotHeight + 20,
        'text-anchor': 'middle',
        fill: 'var(--text)',
        'font-size': '14'
      }, [`Breakwater: ${breakwaterStart.toFixed(1)}m - ${breakwaterEnd.toFixed(1)}m`]));
      
      // Height dimensions - position right under the crest
      g.appendChild(svg('text', {
        x: (bwStart + bwEnd) / 2,
        y: bwY + 15,
        'text-anchor': 'middle',
        fill: 'var(--subtext0)',
        'font-size': '12'
      }, [`Height: ${config.breakwater.crest_height}m`]));
    }
    
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
        
        // Extend gauge lines to a moderate height above water
        // Original was waterY - 10, full extension was 0.2 * actualPlotHeight
        // So halfway between those positions
        const gaugeTop = waterY - ((waterY - actualPlotHeight * 0.2) / 2);
        
        g.appendChild(svg('line', {
          x1: x,
          y1: gaugeTop,
          x2: x,
          y2: actualPlotHeight,
          stroke: 'var(--yellow)',
          'stroke-width': 1,
          'stroke-dasharray': '2,2'
        }));
        g.appendChild(svg('text', {
          x: x,
          y: gaugeTop - 5,
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
    
    // Store the SVG element for export
    currentSvgEl = svgEl;
    
    svgContainer.appendChild(svgEl);
    svgContainer.appendChild(overlayEl);
    container.appendChild(svgContainer);
    
    // Attach export button event listeners
    document.getElementById('export-svg-btn')?.addEventListener('click', exportSVG);
    document.getElementById('export-png-btn')?.addEventListener('click', exportPNG);
    
    // Set initial scroll position centered on the breakwater after DOM update
    requestAnimationFrame(() => {
      if (breakwaterEnabled) {
        const breakwaterCenter = (breakwaterStart + breakwaterEnd) / 2;
        const breakwaterCenterInSvg = (breakwaterCenter - fullDiagramStart) * scale + margin.left;
        const viewportCenter = svgContainer.clientWidth / 2;
        const centerScrollOffset = breakwaterCenterInSvg - viewportCenter;
        svgContainer.scrollLeft = Math.max(0, centerScrollOffset);
      } else {
        // Center on channel middle if no breakwater
        const channelCenter = fullDiagramLength / 2;
        const channelCenterInSvg = (channelCenter - fullDiagramStart) * scale + margin.left;
        const viewportCenter = svgContainer.clientWidth / 2;
        const centerScrollOffset = channelCenterInSvg - viewportCenter;
        svgContainer.scrollLeft = Math.max(0, centerScrollOffset);
      }
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
