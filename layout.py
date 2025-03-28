import dash_html_components as html

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
    "fontSize": "24px"
}

# Predefine lattice parameter blocks for up to 5 CIF files.
# Each block is initially hidden (display: none).
max_files = 5
lattice_params_blocks = []
for i in range(1, max_files + 1):
    block = html.Div(
        id=f"lattice-params-{i}",
        style={
            "position": "relative",  # to allow absolute positioning of the buttons
            "border": "1px solid #ccc",
            "padding": "20px",  # increased padding for a bigger window
            "marginBottom": "10px",
            "display": "none",
            "fontSize": "24px"  # roughly 1.5× the base size
        },
        children=[
            # Reset and Delete buttons (top-right corner)
            html.Div([
                html.Button(
                    "Reset",
                    id=f"reset-{i}",
                    n_clicks=0,
                    style={
                        "backgroundColor": "#cccccc",
                        "color": "black",
                        "fontSize": "14px",
                        "border": "none",
                        "borderRadius": "4px",
                        "padding": "4px 8px",
                        "width": "60px",
                        "marginRight": "5px"
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
                        "borderRadius": "4px",
                        "padding": "4px 8px",
                        "width": "60px"
                    }
                )
            ], style={"position": "absolute", "top": "10px", "right": "10px", "display": "flex"}),
            html.H4(id=f"lattice-params-header-{i}", children=f"CIF File {i}", style={"textAlign": "center", "marginTop": "0px"}),
            html.Div([
                html.Label("a:"),
                dcc.Input(
                    id=f"lattice-{i}-a",
                    type="number",
                    style={"width": "120px", "height": "32px", "fontSize": "20px"}
                )
            ], style={"display": "inline-block", "marginRight": "10px"}),
            html.Div([
                html.Label("b:"),
                dcc.Input(
                    id=f"lattice-{i}-b",
                    type="number",
                    style={"width": "120px", "height": "32px", "fontSize": "20px"}
                )
            ], style={"display": "inline-block", "marginRight": "10px"}),
            html.Div([
                html.Label("c:"),
                dcc.Input(
                    id=f"lattice-{i}-c",
                    type="number",
                    style={"width": "120px", "height": "32px", "fontSize": "20px"}
                )
            ], style={"display": "inline-block", "marginRight": "10px"}),
            html.Div([
                html.Label("α:"),
                dcc.Input(
                    id=f"lattice-{i}-alpha",
                    type="number",
                    style={"width": "120px", "height": "32px", "fontSize": "20px"}
                )
            ], style={"display": "inline-block", "marginRight": "10px"}),
            html.Div([
                html.Label("β:"),
                dcc.Input(
                    id=f"lattice-{i}-beta",
                    type="number",
                    style={"width": "120px", "height": "32px", "fontSize": "20px"}
                )
            ], style={"display": "inline-block", "marginRight": "10px"}),
            html.Div([
                html.Label("γ:"),
                dcc.Input(
                    id=f"lattice-{i}-gamma",
                    type="number",
                    style={"width": "120px", "height": "32px", "fontSize": "20px"}
                )
            ], style={"display": "inline-block", "marginRight": "10px"}),
            html.Div([
                html.Label("Scaling (%):"),
                dcc.Slider(
                    id=f"lattice-scale-{i}",
                    min=-5,
                    max=5,
                    step=0.1,  # Allow 0.1 increments
                    value=0,
                    marks={j: f"{j}%" for j in range(-5, 6)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={"marginTop": "20px", "marginBottom": "10px"})
        ]
    )
    lattice_params_blocks.append(block)

app.layout = html.Div(
    style={"fontFamily": "Dejavu Sans", "fontSize": "16px"},  # Global font style.
    children=[
        html.H1("XRD Pattern Customizer", style={"fontSize": "32px"}),
        
        # Upload Section for .xy file.
        html.Div([
            html.Div([
                html.Div(
                    dcc.Upload(
                        id="upload-xy",
                        children=html.Div("Drop a .xy file or click to select"),
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
            ], style={"display": "flex", "width": "100%"})
        ], style={"width": "50%", "display": "inline-block", "verticalAlign": "top"}),
        
        # Upload Section for .cif files.
        html.Div([
            html.Div([
                html.Div(
                    dcc.Upload(
                        id="upload-cif",
                        children=html.Div("Drop one or more .cif files or click to select"),
                        multiple=True,
                        accept=".cif",
                        style=upload_style
                    ),
                    style={"width": "90%", "display": "inline-block", "verticalAlign": "top"}
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
            ], style={"display": "flex", "width": "100%"})
        ], style={"width": "50%", "display": "inline-block", "verticalAlign": "top"}),
        
        # Lattice Parameters Container (predefined blocks).
        html.Div(id="lattice-params-container", children=lattice_params_blocks),
        
        # Other controls.
        html.Div([
            html.Div([
                html.Label("Intensity Scaling (0-100):"),
                dcc.Input(id="scaling-input", type="number", value=100, min=0, max=100,
                          style={"width": "120px", "height": "32px", "fontSize": "20px"})
            ], style={"display": "inline-block", "marginRight": "20px"}),
            html.Div([
                html.Label("Background Level (0-100):"),
                dcc.Input(id="background-input", type="number", value=0, min=0, max=100,
                          style={"width": "120px", "height": "32px", "fontSize": "20px"})
            ], style={"display": "inline-block"})
        ], style={"marginTop": "10px", "marginBottom": "10px"}),
        
        html.Div([
            html.Label("Pattern Opacity (0-1):"),
            dcc.Slider(
                id="opacity-slider",
                min=0,
                max=1,
                step=0.1,
                value=0.9,
                marks={i/10: str(i/10) for i in range(11)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={"marginTop": "10px", "marginBottom": "10px"}),
        
        # Download Plot button.
        html.Div([
            html.A(
                html.Button("Download Plot", style={
                    "margin-left": "10px",
                    "padding": "9px 18px",  # Increased from 6px 12px
                    "backgroundColor": "#4CAF50",
                    "color": "white",
                    "border": "none",
                    "borderRadius": "4px",
                    "cursor": "pointer",
                    "fontSize": "20px"  # Increased font size for 1.5× effect
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
        ], id="plot-container", style={"width": "100%", "height": "600px"}),
        
        # Hidden stores.
        dcc.Store(id="cif-store"),
        dcc.Store(id="xy-store")
    ]
)

