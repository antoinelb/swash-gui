from pathlib import Path
from typing import Any

import dash
import plotly.graph_objects as go
from dash import ALL, Input, Output, State, callback, dcc, html

from src import config as config_module
from src.dashboard import components


def feather_icon(name: str, size: int = 16):
    """Create a Feather icon using SVG sprite."""
    return html.Div([
        dcc.Markdown(f"""
        <svg class="feather-icon" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <use href="/assets/feather-sprite.svg#{name}"></use>
        </svg>
        """, dangerously_allow_html=True)
    ], style={
        "display": "inline-flex", 
        "align-items": "center",
        "justify-content": "center"
    })


def create_app():
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    
    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content")
    ])
    
    register_callbacks(app)
    return app


def register_callbacks(app):
    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def display_page(pathname):
        if pathname == "/" or pathname == "/configs":
            return config_list_layout()
        elif pathname and pathname.startswith("/config/"):
            config_name = pathname.split("/")[-1]
            return config_detail_layout(config_name)
        elif pathname == "/create":
            return config_create_layout()
        else:
            return config_list_layout()
    
    @app.callback(
        [Output("config-list", "children"),
         Output("config-count", "children")],
        Input("refresh-configs", "n_clicks"),
        prevent_initial_call=False
    )
    def refresh_config_list(n_clicks):
        configs = get_available_configs()
        config_items = [create_config_item(cfg) for cfg in configs]
        count_text = f"{len(configs)} configurations"
        return config_items, count_text
    
    @app.callback(
        [Output("config-content", "children"),
         Output("breakwater-diagram", "children"),
         Output("simulation-results", "children")],
        [Input("url", "pathname"),
         Input("toggle-edit", "n_clicks")],
        prevent_initial_call=False
    )
    def update_config_detail(pathname, edit_clicks):
        if not pathname or not pathname.startswith("/config/"):
            return "", "", ""
        
        config_name = pathname.split("/")[-1]
        try:
            config_path = Path(f"config/{config_name}.yml")
            if config_path.exists():
                cfg = config_module.read_config(config_path)
                editable = (edit_clicks or 0) % 2 == 1
                
                config_display = components.create_config_display(cfg, editable)
                diagram = components.create_breakwater_diagram_placeholder()
                results = components.create_results_placeholder()
                
                return config_display, diagram, results
        except Exception:
            pass
        
        return "Configuration not found", "", ""
    
    @app.callback(
        Output("url", "pathname"),
        Input("new-config-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def navigate_to_create(n_clicks):
        return "/create"
    
    @app.callback(
        [Output("config-form", "children"),
         Output("copy-source-options", "children")],
        Input("url", "pathname"),
        prevent_initial_call=False
    )
    def update_create_form(pathname):
        if pathname == "/create":
            # Create options for copying from existing configs
            configs = get_available_configs()
            copy_options = [{"label": "Start from scratch", "value": ""}]
            copy_options.extend([
                {"label": f"Copy from {cfg['name']}", "value": cfg['name']} 
                for cfg in configs
            ])
            
            copy_dropdown = dcc.Dropdown(
                options=copy_options,
                value="",
                id="copy-source-select",
                className="select-input",
                style={"margin-bottom": "24px"}
            )
            
            default_config = config_module.Config(name="new-config")
            form = components.create_config_display(default_config, editable=True)
            
            return form, copy_dropdown
        return "", ""
    
    @app.callback(
        Output("config-form", "children", allow_duplicate=True),
        Input("copy-source-select", "value"),
        prevent_initial_call=True
    )
    def update_form_from_copy_source(source_name):
        if source_name:
            try:
                config_path = Path(f"config/{source_name}.yml")
                if config_path.exists():
                    cfg = config_module.read_config(config_path)
                    cfg.name = "new-config"  # Reset name for new config
                    return components.create_config_display(cfg, editable=True)
            except Exception:
                pass
        
        # Default config if no source or error
        default_config = config_module.Config(name="new-config")
        return components.create_config_display(default_config, editable=True)


def get_available_configs():
    config_dir = Path("config")
    if not config_dir.exists():
        return []
    
    configs = []
    for yaml_file in config_dir.glob("*.yml"):
        try:
            cfg = config_module.read_config(yaml_file)
            configs.append({
                "name": cfg.name,
                "path": str(yaml_file),
                "hash": cfg.hash[:8],
                "config": cfg
            })
        except Exception:
            continue
    
    return sorted(configs, key=lambda x: x["name"])


def create_config_item(cfg_data):
    return html.A([
        html.Div([
            html.H4(cfg_data["name"]),
            html.P(f"Hash: {cfg_data['hash']}", className="config-hash")
        ], className="config-card-content")
    ], href=f"/config/{cfg_data['name']}", className="config-card")


def config_list_layout():
    return html.Div([
        header_layout("Configuration List"),
        
        html.Div([
            html.Div([
                html.H2("Configurations"),
                html.P(id="config-count")
            ], style={"flex": "1"}),
            
            html.Div([
                html.Button([
                    feather_icon("plus"), " New Config"
                ], className="btn btn-blue", id="new-config-btn"),
                
                html.Button([
                    feather_icon("refresh-cw"), " Refresh"
                ], className="btn btn-default", id="refresh-configs", n_clicks=0)
            ], className="flex flex-gap")
        ], className="flex-between nav-container"),
        
        html.Div(id="config-list")
    ], className="page-container")


def config_detail_layout(config_name):
    return html.Div([
        header_layout(f"Configuration: {config_name}"),
        
        html.Div([
            html.A([
                feather_icon("arrow-left"), " Back to List"
            ], href="/configs", className="btn btn-default"),
            
            html.Div([
                html.Button([
                    feather_icon("edit"), " Edit"
                ], className="btn btn-yellow", id="toggle-edit"),
                
                html.Button([
                    feather_icon("play"), " Run Simulation"
                ], className="btn btn-green", id="run-simulation")
            ], className="flex flex-gap")
        ], className="flex-between nav-container"),
        
        html.Div(id="config-content"),
        html.Div(id="breakwater-diagram"),
        html.Div(id="simulation-results")
    ], className="page-container")


def config_create_layout():
    return html.Div([
        header_layout("Create New Configuration"),
        
        html.Div([
            html.A([
                feather_icon("arrow-left"), " Back to List"
            ], href="/configs", className="btn btn-default"),
            
            html.Div([
                html.Button([
                    feather_icon("save"), " Save Config"
                ], className="btn btn-green", id="save-new-config"),
                
                html.Button([
                    feather_icon("x"), " Cancel"
                ], className="btn btn-red", id="cancel-create")
            ], className="flex flex-gap")
        ], className="flex-between nav-container"),
        
        html.Div([
            html.Label("Copy from existing configuration:", className="field-label"),
            html.Div(id="copy-source-options")
        ], className="field-container"),
        
        html.Div(id="config-form")
    ], className="page-container")


def header_layout(title):
    return html.Div([
        html.H1([
            feather_icon("settings"), f" {title}"
        ])
    ], className="header-container")


if __name__ == "__main__":
    app = create_app()
    app.run_server(debug=True, host="127.0.0.1", port=8000)