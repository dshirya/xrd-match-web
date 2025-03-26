import dash
from dash import html, dcc

# Initialize the Dash app.
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("XRD Pattern Customizer"),
    
    # File Upload Section
    html.Div([
        html.H2("File Uploads"),
        html.Div([
            html.Div([
                html.H3("Upload .xy File"),
                dcc.Upload(
                    id="upload-xy",
                    children=html.Div("Drag and drop or click to select a .xy file"),
                    multiple=False,
                    accept=".xy",
                    style={
                        "border": "1px dashed #ccc",
                        "padding": "10px",
                        "cursor": "pointer"
                    }
                ),
                # Span for check mark status when .xy file is uploaded
                html.Span(id="xy-upload-status", style={
                    "margin-left": "10px",
                    "color": "green",
                    "fontSize": "24px"
                })
            ], style={"flex": "1", "margin-right": "10px"}),
            html.Div([
                html.H3("Upload .cif Files"),
                dcc.Upload(
                    id="upload-cif",
                    children=html.Div("Drag and drop or click to select one or more .cif files"),
                    multiple=True,  # Enables multiple file uploads
                    accept=".cif",
                    style={
                        "border": "1px dashed #ccc",
                        "padding": "10px",
                        "cursor": "pointer"
                    }
                ),
                # Span for displaying a check mark when at least one .cif file is uploaded.
                html.Span(id="cif-upload-status", style={
                    "margin-left": "10px",
                    "color": "green",
                    "fontSize": "24px"
                })
            ], style={"flex": "1", "margin-left": "10px"})
        ], style={"display": "flex", "flexDirection": "row", "alignItems": "center"})
    ], style={"margin-bottom": "20px"}),
    
    # Dropdown to select a CIF file (populated after upload)
    html.Div([
        html.Label("Select CIF File:"),
        dcc.Dropdown(
            id="cif-selector",
            options=[],
            value=None,
            placeholder="Select a CIF file"
        )
    ], style={"margin-bottom": "20px"}),
    
    # Lattice Parameter Inputs
    html.Div([
        html.H2("Lattice Parameters"),
        html.Div([
            html.Label("a:"), dcc.Input(id="a-input", type="number", placeholder="a")
        ], style={"display": "inline-block", "margin-right": "10px"}),
        html.Div([
            html.Label("b:"), dcc.Input(id="b-input", type="number", placeholder="b")
        ], style={"display": "inline-block", "margin-right": "10px"}),
        html.Div([
            html.Label("c:"), dcc.Input(id="c-input", type="number", placeholder="c")
        ], style={"display": "inline-block", "margin-right": "10px"}),
        html.Div([
            html.Label("α:"), dcc.Input(id="alpha-input", type="number", placeholder="α")
        ], style={"display": "inline-block", "margin-right": "10px"}),
        html.Div([
            html.Label("β:"), dcc.Input(id="beta-input", type="number", placeholder="β")
        ], style={"display": "inline-block", "margin-right": "10px"}),
        html.Div([
            html.Label("γ:"), dcc.Input(id="gamma-input", type="number", placeholder="γ")
        ], style={"display": "inline-block"})
    ], style={"margin-top": "20px", "margin-bottom": "20px"}),
    
    # Lattice scaling slider
    html.Div([
        html.Label("Proportional Lattice Scaling (%):"),
        dcc.Slider(
            id="lattice-scale-slider",
            min=-5,
            max=5,
            step=0.1,
            value=0,
            marks={-5: "-5%", -2.5: "-2.5%", 0: "0%", 2.5: "2.5%", 5: "5%"},
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ], style={"margin-top": "20px", "margin-bottom": "20px"}),
    
    # Other controls: intensity scaling, background level, opacity
    html.Div([
        html.Div([
            html.Label("Intensity Scaling (0-100):"),
            dcc.Input(id="scaling-input", type="number", value=100, min=0, max=100)
        ], style={"display": "inline-block", "margin-right": "20px"}),
        html.Div([
            html.Label("Background Level (0-100):"),
            dcc.Input(id="background-input", type="number", value=0, min=0, max=100)
        ], style={"display": "inline-block"})
    ], style={"margin-top": "10px", "margin-bottom": "10px"}),
    
    html.Div([
        html.Label("Pattern Opacity (0-1):"),
        dcc.Slider(
            id="opacity-slider",
            min=0,
            max=1,
            step=0.1,
            value=0.9,
            marks={i/10: str(i/10) for i in range(11)}
        )
    ], style={"margin-top": "10px", "margin-bottom": "10px"}),
    
    # Buttons and download link
    html.Div([
        html.Button("Show CIF Summary", id="show-summary-button", n_clicks=0),
        html.A(
            html.Button("Download Plot", style={
                "margin-left": "10px",
                "padding": "6px 12px",
                "backgroundColor": "#4CAF50",
                "color": "white",
                "border": "none",
                "borderRadius": "4px",
                "cursor": "pointer"
            }),
            id="download-link",
            download="xrd_pattern.png",
            href="",
            target="_blank"
        )
    ], style={"margin-top": "10px", "margin-bottom": "10px"}),
    
    # Display CIF summary
    html.Div(id="cif-summary", style={"margin-top": "20px", "whiteSpace": "pre-wrap"}),
    
    # Container for the Plotly figure
    html.Div([
        dcc.Graph(id="xrd-plot")
    ], id="plot-container", style={"width": "100%", "height": "600px"}),

    # Stores to keep uploaded file data
    dcc.Store(id="cif-store"),
    dcc.Store(id="xy-store")
])