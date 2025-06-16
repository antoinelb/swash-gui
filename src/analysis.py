from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import polars as pl

from src.utils.plotting import colours, template
from src.wave_analysis import calculate_wave_statistics_for_gauges

from .config import Config

############
# external #
############


def analyze_simulation(simulation_dir: Path, config: Config) -> dict:
    """
    Analyze simulation results and generate plots.

    Parameters
    ----------
    simulation_dir : Path
        Directory containing simulation results
    config : Config
        Configuration object for the simulation

    Returns
    -------
    dict
        Analysis results with plot file paths
    """
    timestep = _find_timestep(simulation_dir)
    data = _read_simulaton_data(config, timestep, simulation_dir)
    _plot_water_levels_and_x_velocities(data, config, timestep, simulation_dir)
    _plot_swash_data(config, simulation_dir)

    # Calculate wave statistics
    wave_stats = calculate_wave_statistics_for_gauges(data, timestep)

    # Save wave statistics to CSV
    analysis_dir = simulation_dir / "analysis"
    analysis_dir.mkdir(exist_ok=True)
    wave_stats.write_csv(analysis_dir / "wave_statistics.csv")

    plot_file = simulation_dir / "analysis" / "water_levels_and_x_velocity.png"
    swash_plot_file = simulation_dir / "analysis" / "swash_diagram.png"
    return {
        "plot_file": str(plot_file) if plot_file.exists() else "",
        "swash_plot_file": (
            str(swash_plot_file) if swash_plot_file.exists() else ""
        ),
        "wave_stats": wave_stats.to_dicts(),
    }


############
# internal #
############


def _find_timestep(path: Path) -> float:
    path = path / "swash" / "INPUT"
    with open(path) as f:
        for line in f:
            if line.strip().startswith("WATLEV"):
                timestep = float(line.split()[4])
                break
    return timestep


def _read_simulaton_data(
    config: Config, timestep: float, path: Path
) -> pl.DataFrame:
    path = path / "swash"
    data = pl.concat(
        [
            pl.from_pandas(
                pd.read_csv(
                    path / f"wg{i+1:02d}.txt",
                    sep=r"\s+",
                    header=None,
                    names=["water_level", "x_velocity", "y_velocity"],
                )
            )
            .with_row_index(name="timestep")
            .with_columns(
                pl.col("timestep") * timestep,
                pl.lit(position).alias("position"),
            )
            for i, position in enumerate(config.numeric.wave_gauge_positions)
        ]
    )
    data.write_csv(path / "data.csv")
    return data


def _plot_water_levels_and_x_velocities(
    data: pl.DataFrame, config: Config, timestep: float, simulation_dir: Path
) -> None:
    path = simulation_dir / "analysis"
    path.mkdir(exist_ok=True)

    data = data.with_columns(
        pl.col("position")
        .cast(pl.String)
        .replace(
            {
                position: f"Gauge {i+1} ({position} m)"
                for i, position in enumerate(
                    config.numeric.wave_gauge_positions
                )
            }
        )
    )

    # Helper function to convert position to gauge index for plotting
    def position_to_gauge_index(
        pos: float, gauge_positions: list[float]
    ) -> float:
        """Convert a physical position (m) to gauge index for plotting"""
        if pos <= gauge_positions[0]:
            return 0
        if pos >= gauge_positions[-1]:
            return len(gauge_positions) - 1

        # Find the two gauges that bracket this position
        for i in range(len(gauge_positions) - 1):
            if gauge_positions[i] <= pos <= gauge_positions[i + 1]:
                # Linear interpolation between gauge indices
                ratio = (pos - gauge_positions[i]) / (
                    gauge_positions[i + 1] - gauge_positions[i]
                )
                return i + ratio

        return 0  # fallback

    traces = [
        go.Box(
            x=data["position"],
            y=data["water_level"],
            showlegend=False,
            marker_color=colours[0],
        ),
        go.Box(
            x=data["position"],
            y=data["x_velocity"],
            showlegend=False,
            yaxis="y2",
            marker_color=colours[0],
        ),
    ]

    layout = {
        "template": template,
        "title": "Water levels and x velocities at each gauge position relative to the still water level",
        "xaxis": {
            "title": "Gauge",
        },
        "yaxis": {
            "title": "Water level (m)",
            "domain": [0, 0.45],
        },
        "yaxis2": {
            "title": "X velocity (m/s)",
            "domain": [0.55, 1],
        },
        "shapes": [],
        "annotations": [],
    }

    # Add breakwater rectangle if enabled
    if config.breakwater.enable:
        breakwater_start = config.breakwater.breakwater_start_position
        breakwater_end = config.breakwater_end_position
        gauge_positions = config.numeric.wave_gauge_positions

        # Convert physical positions to gauge indices
        start_index = position_to_gauge_index(
            breakwater_start, gauge_positions
        )
        end_index = position_to_gauge_index(breakwater_end, gauge_positions)

        # Add rectangle shapes for both subplots
        layout["shapes"].extend(
            [
                # Rectangle for water level plot
                {
                    "type": "rect",
                    "x0": start_index - 0.4,
                    "x1": end_index + 0.4,
                    "y0": 0,
                    "y1": 1,
                    "yref": "y domain",
                    "fillcolor": "lightgray",
                    "opacity": 0.3,
                    "line": {"width": 0},
                    "layer": "below",
                },
                # Rectangle for x velocity plot
                {
                    "type": "rect",
                    "x0": start_index - 0.4,
                    "x1": end_index + 0.4,
                    "y0": 0,
                    "y1": 1,
                    "yref": "y2 domain",
                    "fillcolor": "lightgray",
                    "opacity": 0.3,
                    "line": {"width": 0},
                    "layer": "below",
                },
            ]
        )

        # Add annotations for both subplots
        layout["annotations"].extend(
            [
                # Annotation for water level plot
                {
                    "x": (start_index + end_index) / 2,
                    "y": 0.95,
                    "yref": "y domain",
                    "text": "Breakwater",
                    "showarrow": False,
                    "font": {"color": "#cdd6f4"},
                },
                # Annotation for x velocity plot
                {
                    "x": (start_index + end_index) / 2,
                    "y": 0.95,
                    "yref": "y2 domain",
                    "text": "Breakwater",
                    "showarrow": False,
                    "font": {"color": "#cdd6f4"},
                },
            ]
        )

    fig = go.Figure(traces, layout)

    fig.write_image(path / "water_levels_and_x_velocity.png")
    fig.write_json(path / "water_levels_and_x_velocity.json")


def _plot_swash_data(config: Config, simulation_dir: Path) -> None:
    """
    Create a combined cross-section diagram from SWASH data files.

    Parameters
    ----------
    config : Config
        Configuration object for the simulation
    simulation_dir : Path
        Directory containing simulation results
    """
    swash_dir = simulation_dir / "swash"
    analysis_dir = simulation_dir / "analysis"
    analysis_dir.mkdir(exist_ok=True)

    # Create x-coordinates based on grid configuration
    x = np.linspace(0, config.grid.length, config.grid.nx_cells + 1)

    # Read data files
    def read_data_file(filename: str) -> np.ndarray:
        """Read a SWASH data file and return as numpy array"""
        file_path = swash_dir / filename
        if file_path.exists():
            return np.loadtxt(file_path)
        else:
            return np.zeros(len(x))

    bathymetry = read_data_file("bathymetry.txt")
    structure_height = read_data_file("structure_height.txt")
    porosity = read_data_file("porosity.txt")
    vegetation_density = read_data_file("vegetation_density.txt")

    # Create the plot
    fig = go.Figure()

    # Add bathymetry (seafloor) as baseline
    fig.add_trace(
        go.Scatter(
            x=x,
            y=-bathymetry,
            mode="lines",
            fill="tozeroy",
            name="Seafloor",
            line=dict(color=colours[3], width=2),
            fillcolor=colours[3],
            opacity=0.8,
        )
    )

    # Add structure height above seafloor
    structure_top = -bathymetry + structure_height
    fig.add_trace(
        go.Scatter(
            x=x,
            y=structure_top,
            mode="lines",
            fill="tonexty",
            name="Structure",
            line=dict(color=colours[1], width=2),
            fillcolor=colours[1],
            opacity=0.7,
        )
    )

    # Add vegetation density as a layer on top of structure where present
    if config.vegetation.enable and np.any(vegetation_density > 0):
        vegetation_top = (
            structure_top + vegetation_density * 0.5
        )  # Scale vegetation height
        fig.add_trace(
            go.Scatter(
                x=x[vegetation_density > 0],
                y=vegetation_top[vegetation_density > 0],
                mode="lines",
                fill="tonexty",
                name="Vegetation",
                line=dict(color=colours[2], width=2),
                fillcolor=colours[2],
                opacity=0.6,
            )
        )

    # Add water level reference line
    fig.add_hline(
        y=config.water.water_level,
        line_dash="dash",
        line_color=colours[0],
        opacity=0.7,
        annotation_text="Water Level",
        annotation_position="bottom right",
    )

    # Add porosity information as scatter points where structure exists
    if np.any(porosity > 0):
        structure_mask = structure_height > 0
        porosity_x = x[structure_mask]
        porosity_y = (-bathymetry + structure_height / 2)[
            structure_mask
        ]  # Middle of structure
        porosity_values = porosity[structure_mask]

        fig.add_trace(
            go.Scatter(
                x=porosity_x,
                y=porosity_y,
                mode="markers",
                name="Porosity",
                marker=dict(
                    size=8,
                    color=porosity_values,
                    colorscale="Blues",
                    showscale=True,
                    colorbar=dict(title="Porosity", x=1.02),
                    cmin=0,
                    cmax=1,
                ),
                text=[f"Porosity: {p:.2f}" for p in porosity_values],
                hovertemplate="x: %{x:.1f}m<br>Porosity: %{marker.color:.2f}<extra></extra>",
            )
        )

    # Update layout
    fig.update_layout(
        template=template,
        title="SWASH Simulation Cross-Section",
        xaxis_title="Distance (m)",
        yaxis_title="Elevation (m)",
        showlegend=True,
        hovermode="x unified",
        height=500,
    )

    # Save the plot
    fig.write_image(analysis_dir / "swash_diagram.png")
    fig.write_json(analysis_dir / "swash_diagram.json")
