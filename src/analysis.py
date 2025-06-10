from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.subplots
import polars as pl

from src.utils.plotting import colours, template

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
    
    plot_file = simulation_dir / "analysis" / "water_levels_and_x_velocity.png"
    return {"plot_file": str(plot_file) if plot_file.exists() else ""}


############
# internal #
############


def _find_timestep(path: Path) -> float:
    path = path / "swash" / "INPUT"
    with open(path) as f:
        for line in f:
            if line.startswith("COMPUTE"):
                timestep = float(line.split()[2])
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
