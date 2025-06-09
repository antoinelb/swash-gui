import json
from typing import Any

import numpy as np
import plotly.graph_objects as go
import polars as pl

from .config import Config
from .utils.paths import root_dir


def load_wave_gauge_data(config: Config) -> dict[str, pl.DataFrame]:
    """Load wave gauge data from simulation output files.

    Args:
        config: Configuration object containing gauge positions and simulation details

    Returns:
        Dictionary mapping gauge names to Polars DataFrames with columns [time, water_level, u_velocity, v_velocity]
    """
    simulation_dir = root_dir / "simulations" / f"{config.name}_{config.hash}"
    swash_dir = simulation_dir / "swash"
    gauge_data = {}

    for i, position in enumerate(config.numeric.wave_gauge_positions):
        gauge_name = f"wg{i + 1:02d}"
        gauge_file = swash_dir / f"{gauge_name}.txt"

        if not gauge_file.exists():
            continue

        # Load data: columns are [water_level, u_velocity, v_velocity]
        # Time is implicit based on output_interval
        try:
            data = np.loadtxt(gauge_file)
            if data.size == 0:
                continue

            # Create time array
            n_timesteps = len(data)
            time = np.arange(n_timesteps) * config.numeric.output_interval

            # Create Polars DataFrame
            # Convert relative water level to absolute by adding still water level
            absolute_water_level = data[:, 0] + config.water.water_level
            df = pl.DataFrame(
                {
                    "time": time,
                    "water_level": absolute_water_level,
                    "u_velocity": data[:, 1],
                    "v_velocity": data[:, 2],
                    "position": position,
                }
            )

            gauge_data[gauge_name] = df

        except Exception as e:
            print(f"Error loading gauge {gauge_name} from {gauge_file}: {e}")
            continue

    return gauge_data


def _calculate_rolling_stats(data: np.ndarray, window_size: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calculate rolling mean, min, and max for data smoothing.
    
    Args:
        data: Input data array
        window_size: Size of the rolling window
        
    Returns:
        Tuple of (rolling_mean, rolling_min, rolling_max) arrays with same length as input
    """
    if window_size <= 1:
        return data.copy(), data.copy(), data.copy()
    
    # Pad the data to handle edges properly
    padded_data = np.pad(data, window_size//2, mode='edge')
    
    # Calculate rolling statistics
    rolling_mean = np.convolve(padded_data, np.ones(window_size) / window_size, mode='valid')
    
    # For rolling min/max, use sliding window approach
    rolling_min = np.array([
        np.min(padded_data[i:i+window_size]) 
        for i in range(len(padded_data) - window_size + 1)
    ])
    rolling_max = np.array([
        np.max(padded_data[i:i+window_size]) 
        for i in range(len(padded_data) - window_size + 1)
    ])
    
    # Ensure all outputs have same length as input
    for arr in [rolling_mean, rolling_min, rolling_max]:
        if len(arr) != len(data):
            arr = arr[:len(data)]
    
    return rolling_mean, rolling_min, rolling_max


def create_time_series_plot(
    config: Config, gauge_data: dict[str, pl.DataFrame]
) -> dict[str, Any]:
    """Create time series plot of water levels with rolling statistics.

    Args:
        config: Configuration object
        gauge_data: Dictionary of gauge Polars DataFrames from load_wave_gauge_data()

    Returns:
        Plotly figure as JSON-serializable dictionary
    """
    fig = go.Figure()

    # Color palette for different gauges
    colors = ["#89b4fa", "#a6e3a1", "#f9e2af", "#fab387", "#cba6f7", "#f38ba8", "#94e2d5", "#eba0ac"]

    # Add a dummy trace for controlling all filled areas visibility
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=0, color="rgba(0,0,0,0)"),
            name="Wave Range Areas",
            showlegend=True,
            legendgroup="wave_ranges",
            visible=True,
        )
    )

    # Add traces for each gauge
    for i, (gauge_name, df) in enumerate(gauge_data.items()):
        if len(df) == 0:
            continue

        position = df["position"][0]
        time_data = df["time"].to_numpy()
        water_level_data = df["water_level"].to_numpy()

        # Calculate rolling statistics
        # Use window size based on wave period for meaningful averaging
        window_size = max(10, int(config.water.wave_period / config.numeric.output_interval))
        window_size = 50
        rolling_mean, rolling_min, rolling_max = _calculate_rolling_stats(water_level_data, window_size)
        
        # Use color from palette, cycling if needed
        color = colors[i % len(colors)]
        
        # Convert hex color to rgba with transparency (more transparent)
        if color.startswith("#"):
            hex_color = color[1:]  # Remove #
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            translucent_color = f"rgba({r}, {g}, {b}, 0.15)"
        else:
            translucent_color = color
        
        # Add filled area between min and max (translucent)
        fig.add_trace(
            go.Scatter(
                x=np.concatenate([time_data, time_data[::-1]]),
                y=np.concatenate([rolling_max, rolling_min[::-1]]),
                fill="toself",
                fillcolor=translucent_color,
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                name=f"{gauge_name.upper()} Range",
                showlegend=False,
                legendgroup="wave_ranges",
            )
        )
        
        # Calculate midpoint between min and max
        rolling_midpoint = (rolling_min + rolling_max) / 2
        
        # Add rolling midpoint line
        fig.add_trace(
            go.Scatter(
                x=time_data,
                y=rolling_midpoint,
                mode="lines",
                name=f"{gauge_name.upper()} (x={position:.1f}m)",
                line=dict(width=2.5, color=color),
                hovertemplate=(
                    f"<b>{gauge_name.upper()}</b><br>"
                    "Time: %{x:.2f}s<br>"
                    "Midpoint Water Level: %{y:.3f}m<br>"
                    f"Position: {position:.1f}m"
                    "<extra></extra>"
                ),
            )
        )

    # Add still water level reference line
    if gauge_data:
        # Get time range from first gauge
        first_gauge = next(iter(gauge_data.values()))
        time_range = first_gauge["time"].to_numpy()
        
        fig.add_trace(
            go.Scatter(
                x=[time_range[0], time_range[-1]],
                y=[config.water.water_level, config.water.water_level],
                mode="lines",
                name="Still Water Level",
                line=dict(color="white", width=2, dash="dash"),
                hovertemplate=(
                    "<b>Still Water Level</b><br>"
                    "Level: %{y:.3f}m<br>"
                    "<extra></extra>"
                ),
            )
        )

    # Note: Removed spatial breakwater indicator from temporal plot
    # (Breakwater position is spatial, not temporal)

    # Update layout with Catppuccin theme
    fig.update_layout(
        title={
            "text": f"Wave Gauge Time Series - {config.name}",
            "x": 0.5,
            "xanchor": "center",
            "font": {"color": "#cdd6f4", "size": 16},
        },
        xaxis_title="Time (s)",
        yaxis_title="Absolute Water Level (m)",
        hovermode="x unified",
        showlegend=True,
        height=500,
        margin=dict(l=50, r=50, t=70, b=50),
        plot_bgcolor="#313244",  # surface0
        paper_bgcolor="#313244",  # surface0
        font={"color": "#cdd6f4"},  # text
        legend={
            "bgcolor": "rgba(49, 50, 68, 0.8)",  # surface0 with transparency
            "bordercolor": "#585b70",  # surface2
            "borderwidth": 1,
            "font": {"color": "#cdd6f4"},  # text
        },
    )

    # Update axes with Catppuccin theme
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#45475a",  # surface1
        showline=True,
        linewidth=1,
        linecolor="#585b70",  # surface2
        tickfont={"color": "#cdd6f4"},  # text
        title={"font": {"color": "#cdd6f4"}},  # text
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#45475a",  # surface1
        showline=True,
        linewidth=1,
        linecolor="#585b70",  # surface2
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="#6c7086",  # overlay0
        tickfont={"color": "#cdd6f4"},  # text
        title={"font": {"color": "#cdd6f4"}},  # text
    )

    # Convert to JSON-serializable format
    return json.loads(fig.to_json())


def calculate_transmission_coefficient(
    config: Config,
    gauge_data: dict[str, pl.DataFrame],
    incident_gauges: list[str] | None = None,
    transmitted_gauges: list[str] | None = None,
) -> dict[str, float]:
    """Calculate transmission coefficient from wave gauge data.

    Args:
        config: Configuration object
        gauge_data: Dictionary of gauge Polars DataFrames
        incident_gauges: List of gauge names to use for incident waves (default: first 2)
        transmitted_gauges: List of gauge names to use for transmitted waves (default: last 2)

    Returns:
        Dictionary with transmission coefficient and related metrics
    """
    if not gauge_data:
        return {"error": "No gauge data available"}

    gauge_names = sorted(gauge_data.keys())

    # Default gauge selection
    if incident_gauges is None:
        incident_gauges = gauge_names[:2] if len(gauge_names) >= 2 else gauge_names[:1]
    if transmitted_gauges is None:
        transmitted_gauges = (
            gauge_names[-2:] if len(gauge_names) >= 2 else gauge_names[-1:]
        )

    def calculate_wave_height(
        df: pl.DataFrame, duration_seconds: float = 30.0
    ) -> float:
        """Calculate significant wave height from the last portion of the time series."""
        if len(df) == 0:
            return 0.0

        # Use last duration_seconds of data for steady-state analysis
        max_time = df["time"].max()
        if max_time is None:
            return 0.0
        steady_data = df.filter(pl.col("time") >= (max_time - duration_seconds))[
            "water_level"
        ]

        if len(steady_data) < 10:  # Need minimum data points
            return 0.0

        # Calculate RMS wave height (approximate significant wave height)
        std_val = steady_data.std()
        return 4 * float(std_val) if std_val is not None else 0.0

    # Calculate incident wave height (average of incident gauges)
    incident_heights = []
    for gauge in incident_gauges:
        if gauge in gauge_data:
            h = calculate_wave_height(gauge_data[gauge])
            if h > 0:
                incident_heights.append(h)

    # Calculate transmitted wave height (average of transmitted gauges)
    transmitted_heights = []
    for gauge in transmitted_gauges:
        if gauge in gauge_data:
            h = calculate_wave_height(gauge_data[gauge])
            if h > 0:
                transmitted_heights.append(h)

    if not incident_heights or not transmitted_heights:
        return {"error": "Insufficient data for transmission coefficient calculation"}

    h_incident = np.mean(incident_heights)
    h_transmitted = np.mean(transmitted_heights)

    # Calculate transmission coefficient
    kt = h_transmitted / h_incident if h_incident > 0 else 0.0

    return {
        "transmission_coefficient": kt,
        "incident_wave_height": h_incident,
        "transmitted_wave_height": h_transmitted,
        "energy_transmission": kt**2,  # Energy transmission = Kt^2
        "energy_dissipation_percent": (1 - kt**2) * 100,
        "incident_gauges": incident_gauges,
        "transmitted_gauges": transmitted_gauges,
    }


def analyze_simulation(
    config: Config, save_results: bool = True
) -> dict[str, Any]:
    """Complete analysis of simulation results.

    Args:
        config: Configuration object
        save_results: Whether to save results to files in analysis subdirectory

    Returns:
        Dictionary containing all analysis results and visualizations
    """
    # Load gauge data
    gauge_data = load_wave_gauge_data(config)

    if not gauge_data:
        return {"error": "No simulation data found"}

    # Create visualizations
    time_series_plot = create_time_series_plot(config, gauge_data)

    # Calculate metrics
    transmission_results = calculate_transmission_coefficient(config, gauge_data)

    # Prepare results dictionary
    results = {
        "config_name": config.name,
        "config_hash": config.hash,
        "gauge_positions": config.numeric.wave_gauge_positions,
        "breakwater_position": [
            config.numeric.breakwater_start_position,
            config.breakwater_end_position,
        ],
        "time_series_plot": time_series_plot,
        "transmission_analysis": transmission_results,
        "data_summary": {
            "num_gauges": len(gauge_data),
            "gauge_names": list(gauge_data.keys()),
            "simulation_duration": max([df["time"].max() for df in gauge_data.values()])
            if gauge_data
            else 0,
            "data_points_per_gauge": {name: len(df) for name, df in gauge_data.items()},
        },
    }

    # Save results if requested
    if save_results:
        save_analysis_results(config, results)

    return results


def save_analysis_results(
    config: Config, results: dict[str, Any]
) -> None:
    """Save analysis results to files in the analysis subdirectory.

    Args:
        config: Configuration object
        results: Analysis results dictionary from analyze_simulation()
    """
    # Create analysis directory
    simulation_dir = root_dir / "simulations" / f"{config.name}_{config.hash}"
    analysis_dir = simulation_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    # Save metrics as JSON (excluding the plot data)
    metrics = {
        "config_name": results["config_name"],
        "config_hash": results["config_hash"],
        "gauge_positions": results["gauge_positions"],
        "breakwater_position": results["breakwater_position"],
        "transmission_analysis": results["transmission_analysis"],
        "data_summary": results["data_summary"],
    }

    metrics_file = analysis_dir / "metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)

    # Save time series plot
    if "time_series_plot" in results and results["time_series_plot"]:
        try:
            # Reconstruct the Plotly figure from JSON
            fig = go.Figure(results["time_series_plot"])

            # Try to save as PNG first (requires kaleido package)
            try:
                plot_file = analysis_dir / "time_series_plot.png"
                fig.write_image(str(plot_file), width=1200, height=600, scale=2)
            except Exception:
                # If kaleido is not installed, save as HTML instead
                plot_file = analysis_dir / "time_series_plot.html"
                fig.write_html(str(plot_file), include_plotlyjs="cdn")
        except Exception as e:
            print(f"Failed to save plot: {e}")
