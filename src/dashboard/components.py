from dash import html, dcc

from src import config as config_module


def create_config_display(config: config_module.Config, editable: bool = False):
    """Create a display/form for configuration with optional editing."""
    
    sections = [
        create_section("General", [
            create_field("Name", config.name, "name", editable, "text"),
            create_field("Hash", config.hash[:8], "hash", False, "text"),
        ]),
        
        create_section("Computational Grid", [
            create_field("Domain Length (m)", config.grid.length, "grid.length", editable, "number"),
            create_field("Grid Cells (X)", config.grid.nx_cells, "grid.nx_cells", editable, "number"),
            create_field("Vertical Layers", config.grid.n_layers, "grid.n_layers", editable, "number"),
        ]),
        
        create_section("Breakwater", [
            create_field("Start Position (m)", config.numeric.breakwater_start_position, "numeric.breakwater_start_position", editable, "number"),
            create_field("End Position (m)", config.breakwater_end_position, "breakwater.end_position", editable, "number"),
            create_field("Crest Height (m)", config.breakwater.crest_height, "breakwater.crest_height", editable, "number"),
            create_field("Crest Width (m)", config.breakwater.crest_width, "breakwater.crest_width", editable, "number"),
            create_field("Porosity", config.breakwater.porosity, "breakwater.porosity", editable, "number"),
            create_field("Stone Density (kg/m³)", config.breakwater.stone_density, "breakwater.stone_density", editable, "number"),
            create_field("Armour Dn50 (m)", config.breakwater.armour_dn50, "breakwater.armour_dn50", editable, "number"),
            create_field("Slope", config.breakwater.slope, "breakwater.slope", editable, "number"),
        ]),
        
        create_section("Water & Waves", [
            create_field("Water Level (m)", config.water.water_level, "water.water_level", editable, "number"),
            create_field("Water Density (kg/m³)", config.water.water_density, "water.water_density", editable, "number"),
            create_field("Wave Height (m)", config.water.wave_height, "water.wave_height", editable, "number"),
            create_field("Wave Period (s)", config.water.wave_period, "water.wave_period", editable, "number"),
        ]),
        
        create_section("Vegetation", [
            create_field("Enable Vegetation", config.vegetation.enable, "vegetation.enable", editable, "boolean"),
            create_field("Plant Height (m)", config.vegetation.plant_height, "vegetation.plant_height", editable, "number"),
            create_field("Plant Diameter (m)", config.vegetation.plant_diameter, "vegetation.plant_diameter", editable, "number"),
            create_field("Plant Density (/m²)", config.vegetation.plant_density, "vegetation.plant_density", editable, "number"),
            create_field("Drag Coefficient", config.vegetation.drag_coefficient, "vegetation.drag_coefficient", editable, "number"),
        ]),
        
        create_section("Numerical Parameters", [
            create_field("Number of Waves", config.numeric.n_waves, "numeric.n_waves", editable, "number"),
            create_field("Time Step (s)", config.numeric.time_step, "numeric.time_step", editable, "number"),
            create_field("Output Interval (s)", config.numeric.output_interval, "numeric.output_interval", editable, "number"),
            create_array_field("Wave Gauge Positions (m)", config.numeric.wave_gauge_positions, "numeric.wave_gauge_positions", editable),
        ]),
    ]
    
    return html.Div(sections, className="config-content")


def create_section(title: str, fields: list):
    """Create a configuration section with title and fields."""
    return html.Div([
        html.H3(title),
        html.Div(fields, className="config-fields")
    ], className="config-section")


def create_field(label: str, value: any, field_id: str, editable: bool, field_type: str):
    """Create a single configuration field."""
    
    if editable:
        if field_type == "boolean":
            input_component = dcc.Checklist(
                options=[{"label": "", "value": True}],
                value=[True] if value else [],
                id=field_id
            )
        else:
            input_component = dcc.Input(
                type=field_type,
                value=value,
                id=field_id,
                className="field-input"
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
    
    return html.Div([
        html.Label(label, className="field-label"),
        input_component
    ], className="field-container")


def create_array_field(label: str, values: list, field_id: str, editable: bool):
    """Create a field for array values like wave gauge positions."""
    
    if editable:
        input_component = dcc.Input(
            type="text",
            value=", ".join(map(str, values)),
            id=field_id,
            placeholder="Enter comma-separated values",
            className="field-input"
        )
    else:
        display_value = ", ".join(map(str, values))
        input_component = html.Span(
            display_value,
            className="field-display monospace"
        )
    
    return html.Div([
        html.Label(label, className="field-label"),
        input_component
    ], className="field-container")


def create_breakwater_diagram_placeholder():
    """Create a placeholder for the breakwater diagram."""
    return html.Div([
        html.H3("Breakwater Diagram"),
        html.Div([
            html.P("📊 Breakwater visualization will be implemented here", 
                   className="placeholder-text")
        ], className="placeholder-container")
    ])


def create_results_placeholder():
    """Create a placeholder for simulation results."""
    return html.Div([
        html.H3("Simulation Results"),
        html.Div([
            html.P("📈 Simulation results and plots will appear here", 
                   className="placeholder-text")
        ], className="placeholder-container")
    ])