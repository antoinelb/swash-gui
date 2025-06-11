from typing import Any

from dash import html, dcc

from src import config as config_module


def create_config_display(
    config: config_module.Config, editable: bool = False
):
    """Create a display/form for configuration with optional editing."""

    sections = [
        create_section(
            "General",
            [
                create_field("Name", config.name, "name", editable, "text"),
                create_field("Hash", config.hash[:8], "hash", False, "text"),
            ],
        ),
        create_section(
            "Water & Waves",
            [
                create_field(
                    "Water Level (m)",
                    config.water.water_level,
                    "water.water_level",
                    editable,
                    "number",
                ),
                create_field(
                    "Water Density (kg/m³)",
                    config.water.water_density,
                    "water.water_density",
                    editable,
                    "number",
                ),
                create_field(
                    "Wave Height (m)",
                    config.water.wave_height,
                    "water.wave_height",
                    editable,
                    "number",
                ),
                create_field(
                    "Wave Period (s)",
                    config.water.wave_period,
                    "water.wave_period",
                    editable,
                    "number",
                ),
            ],
        ),
        create_section(
            "Numerical Parameters",
            [
                create_field(
                    "Number of Waves",
                    config.numeric.n_waves,
                    "numeric.n_waves",
                    editable,
                    "number",
                ),
                create_array_field(
                    "Wave Gauge Positions (m)",
                    config.numeric.wave_gauge_positions,
                    "numeric.wave_gauge_positions",
                    editable,
                ),
            ],
        ),
    ]

    return html.Div(sections, className="config-content")


def create_section(title: str, fields: list):
    """Create a configuration section with title and fields."""
    return html.Div(
        [html.H3(title), html.Div(fields, className="config-fields")],
        className="config-section",
    )


def create_field(
    label: str, value: Any, field_id: str, editable: bool, field_type: str
):
    """Create a single configuration field."""

    if editable:
        if field_type == "boolean":
            input_component = dcc.Checklist(
                options=[{"label": "", "value": True}],
                value=[True] if value else [],
                id=field_id,
            )
        else:
            input_component = dcc.Input(
                type=field_type,
                value=value,
                id=field_id,
                className="field-input",
            )
    else:
        if field_type == "boolean":
            display_value = "✓ Enabled" if value else "✗ Disabled"
        else:
            display_value = str(value)

        css_classes = "field-display"
        if field_id == "hash":
            css_classes += " monospace"

        input_component = html.Span(display_value, className=css_classes)

    return html.Div(
        [html.Label(label, className="field-label"), input_component],
        className="field-container",
    )


def create_array_field(
    label: str, values: list, field_id: str, editable: bool
):
    """Create a field for array values like wave gauge positions."""

    if editable:
        input_component = dcc.Input(
            type="text",
            value=", ".join(map(str, values)),
            id=field_id,
            placeholder="Enter comma-separated values",
            className="field-input",
        )
    else:
        display_value = ", ".join(map(str, values))
        input_component = html.Span(
            display_value, className="field-display monospace"
        )

    return html.Div(
        [html.Label(label, className="field-label"), input_component],
        className="field-container",
    )


def create_results_placeholder():
    """Create a placeholder for simulation results."""
    return html.Div(
        [
            html.H3("Simulation Results"),
            html.Div(
                [
                    html.P(
                        "📈 Simulation results and plots will appear here",
                        className="placeholder-text",
                    )
                ],
                className="placeholder-container",
            ),
        ]
    )
