import plotly.graph_objects as go

#########
# types #
#########

# Catppuccin Mocha color palette for plotly traces - 10 well-differentiated colors
colours = [
    "#89b4fa",  # blue
    "#f38ba8",  # red
    "#a6e3a1",  # green
    "#fab387",  # peach
    "#cba6f7",  # mauve
    "#94e2d5",  # teal
    "#f9e2af",  # yellow
    "#74c7ec",  # sapphire
    "#eba0ac",  # maroon
    "#b4befe",  # lavender
]


template = {
    "layout": go.Layout(
        {
            "title": {
                "xanchor": "center",
                "x": 0.5,
                "font": {"color": "#cdd6f4", "size": 16},
            },
            "font": {
                "color": "#cdd6f4",
            },
            "xaxis": {
                "gridcolor": "#313244",
                "linecolor": "#a6adc8",
                "automargin": True,
                "title_font": {"color": "#cdd6f4"},
                "tickfont": {"color": "#a6adc8"},
            },
            "yaxis": {
                "gridcolor": "#313244",
                "linecolor": "#a6adc8",
                "automargin": True,
                "title_font": {"color": "#cdd6f4"},
                "tickfont": {"color": "#a6adc8"},
            },
            "paper_bgcolor": "#1e1e2e",  # base
            "plot_bgcolor": "#181825",   # mantle
            "colorway": colours,
            "legend": {
                "font": {"color": "#cdd6f4"},
                "bgcolor": "#313244",  # surface0
                "bordercolor": "#89b4fa",  # blue
                "borderwidth": 1,
            },
            "legend_traceorder": "normal",
            "hovermode": "closest",
        }
    )
}
