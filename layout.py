import dash
from dash import html, dcc

# Initialize the Dash app.
app = dash.Dash(__name__)
server = app.server

# Upload field style.
upload_style = {
    'height': '60px',
    'lineHeight': '60px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '5px',
    'margin': '10px auto',
    'backgroundColor': 'lightgrey',
    'display': 'flex',
    'justifyContent': 'center',
    'alignItems': 'center',
    "fontSize": "24px",
    "fontWeight": "normal"
}

# Set maximum number of CIF files to 8.
max_files = 8

# Predefine lattice parameter blocks for up to 8 CIF files.
lattice_params_blocks = []
for i in range(1, max_files + 1):
    block = html.Div(
        id=f"lattice-params-{i}",
        style={
            "position": "relative",
            "border": "1px solid #ccc",
            "padding": "18px",
            "marginBottom": "8px",
            "display": "none",  # Initially hidden
            "fontSize": "14px",  # Lower font size
            "fontWeight": "normal",
            "width": "100%"
        },
        children=[
            # Reset and Delete buttons (top-right corner)
            html.Div([
                html.Button(
                    "Reset",
                    id=f"reset-{i}",
                    n_clicks=0,
                    style={
                        "backgroundColor": "lightgrey",
                        "color": "white",
                        "fontSize": "14px",
                        "border": "none",
                        "borderRadius": "8px",
                        "padding": "4px 8px",
                        "width": "100px",
                        "marginRight": "10px"
                    }
                ),
                html.Button(
                    "Delete",
                    id=f"delete-{i}",
                    n_clicks=0,
                    style={
                        "backgroundColor": "red",
                        "color": "white",
                        "fontSize": "14px",
                        "border": "none",
                        "borderRadius": "8px",
                        "padding": "4px 8px",
                        "width": "100px"
                    }
                )
            ], style={"position": "absolute", "top": "10px", "right": "10px", "display": "flex"}),
            # Title header placed under the buttons with extra top margin
            html.H4(
                id=f"lattice-params-header-{i}",
                children=f"CIF File {i}",
                style={
                    "textAlign": "center",
                    "marginTop": "50px",  # Added margin so it appears below the buttons
                    "marginBottom": "5px",
                    "fontWeight": "normal",
                    "fontSize": "18px"
                }
            ),
            # Lattice parameters for each block:
            html.Div([
                html.H5(
                    "Cell parameters",
                    style={
                        "textAlign": "center",
                        "marginTop": "0px",
                        "marginBottom": "0px",
                        "paddingTop": "0px",
                        "paddingBottom": "0px",
                        "fontWeight": "normal",
                        "fontSize": "14px"
                    }
                ),
                html.Div([
                    html.Div([
                        html.Label("a:", style={"fontSize": "14px"}),
                        dcc.Input(
                            id=f"lattice-{i}-a",
                            type="number",
                            style={
                                "width": "60px",         # Reduced width
                                "height": "24px",        # Reduced height
                                "fontSize": "14px",      # Lower font size
                                "margin": "5px"          # Reduced margin
                            }
                        )
                    ], style={"display": "inline-block", "marginRight": "5px"}),
                    html.Div([
                        html.Label("b:", style={"fontSize": "14px"}),
                        dcc.Input(
                            id=f"lattice-{i}-b",
                            type="number",
                            style={
                                "width": "60px",         
                                "height": "24px",        
                                "fontSize": "14px",     
                                "margin": "5px"          
                            }
                        )
                    ], style={"display": "inline-block", "marginRight": "5px"}),
                    html.Div([
                        html.Label("c:", style={"fontSize": "14px"}),
                        dcc.Input(
                            id=f"lattice-{i}-c",
                            type="number",
                            style={
                                "width": "60px",         
                                "height": "24px",        
                                "fontSize": "14px",     
                                "margin": "5px"  
                            }
                        )
                    ], style={"display": "inline-block", "marginRight": "5px"}),
                    html.Div([
                        html.Div([
                            html.Label("α:", style={"fontSize": "14px"}),
                            dcc.Input(
                                id=f"lattice-{i}-alpha",
                                type="number",
                                style={
                                    "width": "50px",
                                    "height": "24px",
                                    "fontSize": "14px",
                                    "margin": "5px"
                                }
                            )
                        ], style={"display": "inline-block", "marginRight": "5px"}),
                        html.Div([
                            html.Label("β:", style={"fontSize": "14px"}),
                            dcc.Input(
                                id=f"lattice-{i}-beta",
                                type="number",
                                style={
                                    "width": "50px",
                                    "height": "24px",
                                    "fontSize": "14px",
                                    "margin": "5px"
                                }
                            )
                        ], style={"display": "inline-block", "marginRight": "5px"}),
                        html.Div([
                            html.Label("γ:", style={"fontSize": "14px"}),
                            dcc.Input(
                                id=f"lattice-{i}-gamma",
                                type="number",
                                style={
                                    "width": "50px",
                                    "height": "24px",
                                    "fontSize": "14px",
                                    "margin": "5px"
                                }
                            )
                        ], style={"display": "inline-block", "marginRight": "5px"})
                    ], style={"display": "flex", "alignItems": "center", "fontSize": "14px"})
                ], style={"display": "flex", "flexWrap": "wrap", "gap": "5px"})
            ]),
            html.Div([
                # Intensity scaling slider
                html.Div([
                    html.Label("Intensity scaling:", style={"fontSize": "14px"}),
                    dcc.Slider(
                        id=f"intensity-{i}",
                        min=0,
                        max=100,
                        step=1,
                        value=100,
                        marks={j: str(j) for j in range(0, 101, 10)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], style={"flex": "1 1 200px", "marginRight": "5px", "fontSize": "14px"}),
                # Background level slider
                html.Div([
                    html.Label("Background level:", style={"fontSize": "14px"}),
                    dcc.Slider(
                        id=f"background-{i}",
                        min=0,
                        max=100,
                        step=1,
                        value=0,
                        marks={j: str(j) for j in range(0, 101, 10)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], style={"flex": "1 1 200px", "marginRight": "5px", "fontSize": "14px"}),
                # Shift unit cell slider
                html.Div([
                    html.Label("Shift unit cell:", style={"fontSize": "14px"}),
                    dcc.Slider(
                        id=f"lattice-scale-{i}",
                        min=-5,
                        max=5,
                        step=0.1,
                        value=0,
                        marks={j: f"{j}%" for j in range(-5, 6)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], style={"flex": "1 1 200px", "marginRight": "5px", "fontSize": "14px"})
            ], style={"display": "flex", "flexWrap": "wrap", "gap": "5px"})
        ]
    )
    lattice_params_blocks.append(block)

# Define the overall layout.
app.layout = html.Div(
    style={"fontFamily": "Open Sans", "fontSize": "16px"},
    children=[
        html.Div(
            children=[
                html.H1("XRD Pattern Customizer", style={"fontSize": "32px", "fontWeight": "normal"}),
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "height": "5vh",
                "textAlign": "center"
            }
        ),
        # Upload Section for .xy and .cif files.
        html.Div([
            # XY file upload container.
            html.Div([
                html.Div(
                    dcc.Upload(
                        id="upload-xy",
                        children=html.Div("Drop an .xy file or click to select"),
                        multiple=False,
                        accept=".xy",
                        style=upload_style
                    ),
                    style={"width": "90%", "display": "inline-block", "verticalAlign": "top"}
                ),
                html.Div(
                    html.Span(
                        id="xy-upload-status",
                        style={
                            "margin-left": "10px",
                            "color": "green",
                            "fontSize": "24px",
                            "position": "relative",
                            "textAlign": "center",
                            "left": "20px",
                            "top": "20px"
                        }
                    ),
                    style={"width": "10%", "display": "inline-block", "verticalAlign": "middle"}
                )
            ], style={"width": "50%", "display": "inline-block"}),
            # CIF file upload container.
            html.Div([
                html.Div(
                    dcc.Upload(
                        id="upload-cif",
                        children=html.Div("Drop one or more .cif files or click to select (do this first)"),
                        multiple=True,
                        accept=".cif",
                        style=upload_style
                    ),
                    style={"width": "90%", "display": "inline-block", "verticalAlign": "top", "fontWeight": "normal"}
                ),
                html.Div(
                    html.Span(
                        id="cif-upload-status",
                        style={
                            "margin-left": "10px",
                            "color": "green",
                            "fontSize": "24px",
                            "position": "relative",
                            "textAlign": "center",
                            "left": "20px",
                            "top": "20px"
                        }
                    ),
                    style={"width": "10%", "display": "inline-block", "verticalAlign": "middle"}
                )
            ], style={"width": "50%", "display": "inline-block"})
        ], style={"display": "flex", "width": "100%"}),
        # Lattice Parameters Container (arranged in a grid with up to 4 per row).
        html.Div(
            id="lattice-params-container",
            children=lattice_params_blocks,
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                "gap": "10px",
                "justifyContent": "center"
            }
        ),
        # Global Pattern Opacity control.
        html.Div([
            html.Label("Pattern opacities:"),
            dcc.Slider(
                id="opacity-slider",
                min=0,
                max=1,
                step=0.1,
                value=0.9,
                marks={i/10: str(i*10) for i in range(11)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={"marginTop": "10px", "marginBottom": "10px", "fontSize": "18px", "width": "14.3%", "marginLeft": "21px"}),
        # Download Plot button.
        html.Div([
            html.A(
                html.Button("Download plot", style={
                    "margin-left": "10px",
                    "padding": "9px 18px",
                    "backgroundColor": "#4CAF50",
                    "color": "white",
                    "border": "none",
                    "borderRadius": "4px",
                    "cursor": "pointer",
                    "fontSize": "20px"
                }),
                id="download-link",
                download="xrd_pattern.png",
                href="",
                target="_blank"
            )
        ], style={"marginTop": "10px", "marginBottom": "10px"}),
        # XRD Plot.
        html.Div([
            dcc.Graph(id="xrd-plot")
        ], id="plot-container", style={"width": "100%", "height": "1000px"}),
        # Hidden data stores.
        dcc.Store(id="cif-store"),
        dcc.Store(id="xy-store")
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)