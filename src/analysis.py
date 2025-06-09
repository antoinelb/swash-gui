"""Wave energy analysis for breakwater effect studies.

This module provides functions to analyze wave gauge data and generate plots
showing wave energy characteristics at various positions along a channel.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import plotly.graph_objects as go
import polars as pl

from .config import Config


def load_wave_gauge_data(simulation_dir: Path) -> Dict[str, pl.DataFrame]:
    """Load wave gauge data from SWASH output files.
    
    Args:
        simulation_dir: Path to simulation directory containing swash/ subdirectory
        
    Returns:
        Dictionary mapping gauge names to DataFrames with columns: time, water_level, velocity
    """
    swash_dir = simulation_dir / "swash"
    gauge_data = {}
    
    # Find all wave gauge files (wg01.txt, wg02.txt, etc.)
    for gauge_file in swash_dir.glob("wg*.txt"):
        gauge_name = gauge_file.stem.upper()  # wg01 -> WG01
        
        # Load data using numpy first to handle SWASH's space-separated scientific notation
        try:
            data = np.loadtxt(gauge_file)
            if data.shape[1] >= 3:
                # Convert to polars DataFrame
                df = pl.DataFrame({
                    "time": data[:, 0],
                    "water_level": data[:, 1],
                    "velocity": data[:, 2]
                })
            else:
                continue
        except Exception as e:
            print(f"Warning: Could not load {gauge_file}: {e}")
            continue
        
        gauge_data[gauge_name] = df
    
    return gauge_data


def calculate_significant_wave_height(water_levels: np.ndarray, dt: float, window_duration: float = 1800.0) -> float:
    """Calculate significant wave height using zero-crossing method.
    
    Args:
        water_levels: Water level time series
        dt: Time step
        window_duration: Analysis window duration in seconds (default 30 min)
        
    Returns:
        Significant wave height (Hs)
    """
    # Check for valid dt
    if dt <= 0 or np.isnan(dt) or np.isinf(dt):
        return 0.0
    
    # Use last window_duration seconds of data
    n_window = int(window_duration / dt)
    if len(water_levels) > n_window:
        water_levels = water_levels[-n_window:]
    
    # Remove mean to focus on wave oscillations
    water_levels = water_levels - np.mean(water_levels)
    
    # Find zero-crossings (upward)
    zero_crossings = []
    for i in range(1, len(water_levels)):
        if water_levels[i-1] <= 0 < water_levels[i]:
            zero_crossings.append(i)
    
    if len(zero_crossings) < 2:
        return 0.0
    
    # Extract wave heights between zero-crossings
    wave_heights = []
    for i in range(len(zero_crossings) - 1):
        start_idx = zero_crossings[i]
        end_idx = zero_crossings[i + 1]
        wave_segment = water_levels[start_idx:end_idx]
        
        # Wave height = max - min in this segment
        if len(wave_segment) > 0:
            wave_height = np.max(wave_segment) - np.min(wave_segment)
            wave_heights.append(wave_height)
    
    if not wave_heights:
        return 0.0
    
    # Significant wave height = average of highest 1/3 of waves
    wave_heights = sorted(wave_heights, reverse=True)
    n_significant = max(1, len(wave_heights) // 3)
    hs = np.mean(wave_heights[:n_significant])
    
    return hs


def calculate_gauge_metrics(gauge_data: Dict[str, pl.DataFrame], 
                           gauge_positions: List[float],
                           config: Config) -> Dict[str, Dict]:
    """Calculate key wave metrics at each gauge position.
    
    Args:
        gauge_data: Wave gauge data
        gauge_positions: X-positions of wave gauges
        config: Simulation configuration
        
    Returns:
        Dictionary mapping gauge names to metrics dictionaries
    """
    gauge_metrics = {}
    
    for i, (gauge_name, df) in enumerate(gauge_data.items()):
        water_levels = df["water_level"].to_numpy()
        times = df["time"].to_numpy()
        velocity = df["velocity"].to_numpy()
        
        # Calculate time step with error handling
        if len(times) > 1:
            dt = times[1] - times[0]
            if dt <= 0 or np.isnan(dt) or np.isinf(dt):
                dt = 0.1
        else:
            dt = 0.1
        
        # Position from config (with fallback)
        position = gauge_positions[i] if i < len(gauge_positions) else 0.0
        
        # Calculate metrics
        hs = calculate_significant_wave_height(water_levels, dt)
        mean_level = np.mean(water_levels)
        max_level = np.max(water_levels)
        min_level = np.min(water_levels)
        rms_level = np.sqrt(np.mean(water_levels**2))
        max_velocity = np.max(np.abs(velocity))
        
        # Wave setup (mean water level change from reference)
        setup = mean_level - config.water.water_level if hasattr(config.water, 'water_level') else mean_level
        
        gauge_metrics[gauge_name] = {
            'position': position,
            'significant_wave_height': hs,
            'mean_water_level': mean_level,
            'wave_setup': setup,
            'max_water_level': max_level,
            'min_water_level': min_level,
            'rms_water_level': rms_level,
            'max_velocity': max_velocity,
            'wave_amplitude': (max_level - min_level) / 2
        }
    
    return gauge_metrics


def calculate_transmission_coefficients(gauge_data: Dict[str, pl.DataFrame],
                                      gauge_positions: List[float],
                                      config: Config) -> Dict[str, float]:
    """Calculate transmission coefficients relative to first gauge.
    
    Args:
        gauge_data: Wave gauge data
        gauge_positions: X-positions of wave gauges
        config: Simulation configuration
        
    Returns:
        Dictionary mapping gauge names to transmission coefficients
    """
    # Sort gauges by position
    gauge_info = [(name, pos) for name, pos in zip(gauge_data.keys(), gauge_positions)]
    gauge_info.sort(key=lambda x: x[1])
    
    if not gauge_info:
        return {}
    
    # Calculate Hs for each gauge
    wave_heights = {}
    for gauge_name, df in gauge_data.items():
        water_levels = df["water_level"].to_numpy()
        times = df["time"].to_numpy()
        
        # Calculate time step with error handling
        if len(times) > 1:
            dt = times[1] - times[0]
            if dt <= 0 or np.isnan(dt) or np.isinf(dt):
                dt = 0.1
        else:
            dt = 0.1
        
        hs = calculate_significant_wave_height(water_levels, dt)
        wave_heights[gauge_name] = hs
    
    # Reference gauge (first/incident)
    reference_gauge = gauge_info[0][0]
    reference_hs = wave_heights.get(reference_gauge, 1.0)
    
    if reference_hs == 0:
        reference_hs = 1.0  # Avoid division by zero
    
    # Calculate transmission coefficients
    transmission_coeffs = {}
    for gauge_name in gauge_data.keys():
        hs = wave_heights.get(gauge_name, 0.0)
        kt = hs / reference_hs
        transmission_coeffs[gauge_name] = kt
    
    return transmission_coeffs




def create_wave_envelope_plot(gauge_data: Dict[str, pl.DataFrame],
                             gauge_positions: List[float],
                             gauge_metrics: Dict[str, Dict],
                             config: Config,
                             output_dir: Path) -> str:
    """Create wave envelope plot along the channel.
    
    Args:
        gauge_data: Wave gauge data
        gauge_positions: X-positions of wave gauges
        gauge_metrics: Calculated metrics for each gauge
        config: Simulation configuration
        output_dir: Directory to save plot
        
    Returns:
        Path to the generated plot file
    """
    output_dir.mkdir(exist_ok=True)
    
    # Extract positions and wave heights from metrics, sorted by position
    sorted_metrics = sorted(gauge_metrics.items(), 
                          key=lambda x: x[1]['position'])
    
    positions = [metrics['position'] for _, metrics in sorted_metrics]
    wave_heights = [metrics['significant_wave_height'] for _, metrics in sorted_metrics]
    wave_amplitudes = [metrics['wave_amplitude'] for _, metrics in sorted_metrics]
    gauge_names = [name for name, _ in sorted_metrics]
    
    # Create the plot
    fig = go.Figure()
    
    # Add wave envelope (significant wave height)
    fig.add_trace(go.Scatter(
        x=positions,
        y=wave_heights,
        mode='lines+markers',
        name='Significant Wave Height (Hs)',
        line=dict(width=3, color='blue'),
        marker=dict(size=10, color='blue'),
        hovertemplate='<b>%{text}</b><br>' +
                      'Position: %{x:.1f} m<br>' +
                      'Hs: %{y:.3f} m<br>' +
                      '<extra></extra>',
        text=gauge_names
    ))
    
    # Add wave amplitude for comparison
    fig.add_trace(go.Scatter(
        x=positions,
        y=wave_amplitudes,
        mode='lines+markers',
        name='Wave Amplitude (A)',
        line=dict(width=2, color='lightblue', dash='dash'),
        marker=dict(size=8, color='lightblue'),
        hovertemplate='<b>%{text}</b><br>' +
                      'Position: %{x:.1f} m<br>' +
                      'Amplitude: %{y:.3f} m<br>' +
                      '<extra></extra>',
        text=gauge_names
    ))
    
    # Add annotations for each gauge with key metrics
    for i, (name, metrics) in enumerate(sorted_metrics):
        pos = metrics['position']
        hs = metrics['significant_wave_height']
        setup = metrics['wave_setup']
        
        fig.add_annotation(
            x=pos,
            y=hs + 0.05,  # Slightly above the point
            text=f"{name}<br>Hs: {hs:.3f}m<br>Setup: {setup:.3f}m",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="darkblue",
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="darkblue",
            borderwidth=1,
            font=dict(size=10)
        )
    
    # Add reference line at incident wave height if available
    if hasattr(config.water, 'wave_height'):
        incident_height = config.water.wave_height
        fig.add_hline(
            y=incident_height,
            line_dash="dot",
            line_color="red",
            annotation_text=f"Incident Wave Height = {incident_height}m",
            annotation_position="top right"
        )
    
    # Customize layout
    fig.update_layout(
        title={
            'text': f"Wave Envelope Along Channel - {config.name}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title="Distance Along Channel (m)",
        yaxis_title="Wave Height (m)",
        template="plotly_white",
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1
        ),
        hovermode='closest',
        width=900,
        height=600
    )
    
    # Set axis ranges
    fig.update_xaxes(range=[min(positions) - 5, max(positions) + 5])
    fig.update_yaxes(range=[0, max(wave_heights) * 1.2])
    
    # Save plot as PNG
    plot_file = output_dir / "wave_envelope.png"
    fig.write_image(plot_file, width=900, height=600, scale=2)
    
    return str(plot_file)


def analyze_simulation(simulation_dir: Path, config: Config) -> Dict:
    """Analyze wave data for a completed simulation.
    
    Args:
        simulation_dir: Path to simulation directory
        config: Simulation configuration
        
    Returns:
        Dictionary containing analysis results and plot file paths
    """
    # Load wave gauge data
    gauge_data = load_wave_gauge_data(simulation_dir)
    
    if not gauge_data:
        return {"error": "No wave gauge data found"}
    
    # Get gauge positions from config
    gauge_positions = config.numeric.wave_gauge_positions
    
    # Create analysis output directory
    analysis_dir = simulation_dir / "analysis"
    analysis_dir.mkdir(exist_ok=True)
    
    # Calculate gauge metrics
    gauge_metrics = calculate_gauge_metrics(gauge_data, gauge_positions, config)
    
    # Generate wave envelope plot
    plot_file = create_wave_envelope_plot(gauge_data, gauge_positions, gauge_metrics, config, analysis_dir)
    
    # Calculate transmission coefficients for reference
    transmission_coeffs = calculate_transmission_coefficients(gauge_data, gauge_positions, config)
    
    # Create summary report
    analysis_results = {
        "gauge_metrics": gauge_metrics,
        "transmission_coefficients": transmission_coeffs,
        "plot_file": plot_file,
        "config_hash": config.hash,
        "analysis_timestamp": str(np.datetime64('now'))
    }
    
    # Save analysis results
    results_file = analysis_dir / "analysis_results.json"
    with open(results_file, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    return analysis_results


if __name__ == "__main__":
    # Example usage
    from .config import Config
    
    config_path = Path("config/dev.yml")
    simulation_dir = Path("simulations/example_simulation")
    
    if config_path.exists() and simulation_dir.exists():
        config = Config.from_file(config_path)
        results = analyze_simulation(simulation_dir, config)
        print(f"Analysis complete. Results saved to: {simulation_dir}/analysis/")
        print(f"Generated plots: {list(results.get('plot_files', {}).keys())}")
