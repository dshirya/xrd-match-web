import dash
from dash import html, dcc

# Initialize the Dash app.
app = dash.Dash(__name__)
server = app.server

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
    'alignItems': 'center'
}

app.layout = html.Div(
    style={"fontFamily": "Dejavu Sans", "fontSize": "16px"},  # Global font style for all text.
    children=[
        html.H1("XRD Pattern Customizer", style={"fontSize": "32px"}),

        # File Upload Section with specified width percentages:
        html.Div([
            # .xy File Upload (45% drop field)
            html.Div([
                html.H3("Upload .xy File", style={"fontSize": "20px", "marginBottom": "5px", "textAlign": "center"}),
                dcc.Upload(
                    id="upload-xy",
                    children=html.Div("Drop a .xy file or click to select "),
                    multiple=False,
                    accept=".xy",
                    style=upload_style
                )
            ], style={"width": "45%", "display": "inline-block", "verticalAlign": "top"}),

            # Tick mark for .xy file (5%)
            html.Div([
                html.Span(
                    id="xy-upload-status",
                    style={
                        "margin-left": "10px",
                        "color": "green",
                        "fontSize": "24px",
                        "position": "relative",
                        "textAlign": "center",
                        "left": "20px",  # Adjust this value to move the tick mark right
                        "top": "20px"  # Adjust this value to move the tick mark lower
                    }
                )
            ], style={"width": "5%", "display": "inline-block", "verticalAlign": "middle"}),

            # .cif File Upload (45% drop field)
            html.Div([
                html.H3("Upload .cif Files", style={"fontSize": "20px", "marginBottom": "5px", "textAlign": "center"}),
                dcc.Upload(
                    id="upload-cif",
                    children=html.Div("Drop one or more .cif files or click to select"),
                    multiple=True,  # Enables multiple file uploads
                    accept=".cif",
                    style=upload_style
                )
            ], style={"width": "45%", "display": "inline-block", "verticalAlign": "top"}),

            # Tick mark for .cif file (5%)
            html.Div([
                html.Span(id="cif-upload-status", style={
                        "margin-left": "10px",
                        "color": "green",
                        "fontSize": "24px",
                        "position": "relative",
                        "textAlign": "center",
                        "left": "20px",  # Adjust this value to move the tick mark right
                        "top": "20px"
                })
            ], style={"width": "5%", "display": "inline-block", "verticalAlign": "middle"})
        ], style={"width": "100%", "display": "flex", "alignItems": "center", "marginBottom": "20px"}),

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
            html.H2("Lattice Parameters", style={"fontSize": "28px"}),
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
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)