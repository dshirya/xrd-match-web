import base64
import pandas as pd
import json
from dash import Input, Output, State, no_update
import plotly.graph_objects as go
from layout import app, max_files  # import max_files from layout (max_files = 8)
from preprocess import parse_xy, parse_cif, normalize_structure, XRDCalculator
from plot import plot_xrd
from pymatgen.core import Structure
import plotly.io as pio

# ------------------------------------------------------------------
# File Upload Check Mark Callbacks
# ------------------------------------------------------------------
@app.callback(
    Output("xy-upload-status", "children"),
    Input("upload-xy", "contents")
)
def update_xy_status(contents):
    if contents:
        return "✓"
    return ""

@app.callback(
    Output("cif-upload-status", "children"),
    Input("upload-cif", "contents")
)
def update_cif_status(contents_list):
    if contents_list:
        return "✓"
    return ""

# ------------------------------------------------------------------
# Store Uploaded Files Callbacks
# ------------------------------------------------------------------
@app.callback(
    Output("xy-store", "data"),
    Input("upload-xy", "contents"),
    State("upload-xy", "filename")
)
def store_xy_file(contents, filename):
    if contents is not None:
        try:
            df = parse_xy(contents)
            max_intensity = df['intensity'].max()
            df['intensity'] = (df['intensity'] / max_intensity) * 100
            return df.to_json(date_format='iso', orient='split')
        except Exception as e:
            print("Error processing XY file:", e)
            return no_update
    return no_update

@app.callback(
    Output("cif-store", "data"),
    Input("upload-cif", "contents"),
    State("upload-cif", "filename")
)
def store_cif_files(contents_list, filenames):
    if contents_list is not None:
        cif_data = {}
        for contents, name in zip(contents_list, filenames):
            try:
                cif_data[name] = contents
            except Exception as e:
                print("Error processing CIF file:", e)
        return cif_data
    return no_update

# ------------------------------------------------------------------
# Lattice Parameter Blocks Update Callback (for 8 blocks)
# ------------------------------------------------------------------
@app.callback(
    [Output(f"lattice-params-{i}", "style") for i in range(1, max_files+1)] +
    [Output(f"lattice-params-header-{i}", "children") for i in range(1, max_files+1)] +
    [Output(f"lattice-{i}-a", "value") for i in range(1, max_files+1)] +
    [Output(f"lattice-{i}-b", "value") for i in range(1, max_files+1)] +
    [Output(f"lattice-{i}-c", "value") for i in range(1, max_files+1)] +
    [Output(f"lattice-{i}-alpha", "value") for i in range(1, max_files+1)] +
    [Output(f"lattice-{i}-beta", "value") for i in range(1, max_files+1)] +
    [Output(f"lattice-{i}-gamma", "value") for i in range(1, max_files+1)],
    Input("cif-store", "data")
)
def update_lattice_params_blocks(cif_data):
    style_outputs = []
    header_outputs = []
    a_outputs = []
    b_outputs = []
    c_outputs = []
    alpha_outputs = []
    beta_outputs = []
    gamma_outputs = []
    
    file_names = sorted(cif_data.keys()) if cif_data else []
    num_files = len(file_names)
    
    for i in range(max_files):
        if i < num_files:
            try:
                structure = parse_cif(cif_data[file_names[i]])
                structure = normalize_structure(structure)
                lattice = structure.lattice
                style_outputs.append({
                    "display": "inline-block",
                    "width": "90%",
                    "marginRight": "10px",
                    "position": "relative",
                    "border": "1px solid #ccc",
                    "padding": "20px",
                    "marginBottom": "10px",
                    "fontSize": "24px"
                })
                header_outputs.append(file_names[i])
                a_outputs.append(round(lattice.a, 4))
                b_outputs.append(round(lattice.b, 4))
                c_outputs.append(round(lattice.c, 4))
                alpha_outputs.append(round(lattice.alpha, 4))
                beta_outputs.append(round(lattice.beta, 4))
                gamma_outputs.append(round(lattice.gamma, 4))
            except Exception as e:
                print("Error parsing CIF for lattice block:", e)
                style_outputs.append({"display": "none"})
                header_outputs.append("")
                a_outputs.append(None)
                b_outputs.append(None)
                c_outputs.append(None)
                alpha_outputs.append(None)
                beta_outputs.append(None)
                gamma_outputs.append(None)
        else:
            style_outputs.append({"display": "none"})
            header_outputs.append("")
            a_outputs.append(None)
            b_outputs.append(None)
            c_outputs.append(None)
            alpha_outputs.append(None)
            beta_outputs.append(None)
            gamma_outputs.append(None)
    
    return style_outputs + header_outputs + a_outputs + b_outputs + c_outputs + alpha_outputs + beta_outputs + gamma_outputs

# ------------------------------------------------------------------
# Reset Button Callbacks (One per block)
# ------------------------------------------------------------------
def make_reset_callback(i):
    @app.callback(
        [Output(f"lattice-{i}-a", "value", allow_duplicate=True),
         Output(f"lattice-{i}-b", "value", allow_duplicate=True),
         Output(f"lattice-{i}-c", "value", allow_duplicate=True),
         Output(f"lattice-{i}-alpha", "value", allow_duplicate=True),
         Output(f"lattice-{i}-beta", "value", allow_duplicate=True),
         Output(f"lattice-{i}-gamma", "value", allow_duplicate=True)],
        Input(f"reset-{i}", "n_clicks"),
        [State("cif-store", "data"),
         State(f"lattice-params-header-{i}", "children")],
        prevent_initial_call='initial_duplicate'
    )
    def reset_block(n_clicks, cif_data, file_name):
        if not cif_data or not file_name:
            return no_update, no_update, no_update, no_update, no_update, no_update
        try:
            structure = parse_cif(cif_data[file_name])
            structure = normalize_structure(structure)
            lattice = structure.lattice
            return (
                round(lattice.a, 4),
                round(lattice.b, 4),
                round(lattice.c, 4),
                round(lattice.alpha, 4),
                round(lattice.beta, 4),
                round(lattice.gamma, 4)
            )
        except Exception as e:
            print("Error in reset callback for", file_name, ":", e)
            return no_update, no_update, no_update, no_update, no_update, no_update
    return reset_block

for i in range(1, max_files+1):
    make_reset_callback(i)

# ------------------------------------------------------------------
# Delete Button Callbacks (One per block)
# ------------------------------------------------------------------
def make_delete_callback(i):
    @app.callback(
        Output("cif-store", "data", allow_duplicate=True),
        Input(f"delete-{i}", "n_clicks"),
        [State("cif-store", "data"),
         State(f"lattice-params-header-{i}", "children")],
        prevent_initial_call='initial_duplicate'
    )
    def delete_block(n_clicks, cif_data, file_name):
        if not cif_data or not file_name:
            return no_update
        if n_clicks and file_name in cif_data:
            new_data = cif_data.copy()
            new_data.pop(file_name)
            return new_data
        return cif_data
    return delete_block

for i in range(1, max_files+1):
    make_delete_callback(i)

# ------------------------------------------------------------------
# XRD Plot Callback (Using Dynamic Lattice Parameters and per-CIF intensity/background)
# ------------------------------------------------------------------
@app.callback(
    Output("xrd-plot", "figure"),
    [
        Input("xy-store", "data"),
        Input("opacity-slider", "value"),
        # Lattice parameter inputs for blocks 1 to 8.
        # a parameters
        Input("lattice-1-a", "value"),
        Input("lattice-2-a", "value"),
        Input("lattice-3-a", "value"),
        Input("lattice-4-a", "value"),
        Input("lattice-5-a", "value"),
        Input("lattice-6-a", "value"),
        Input("lattice-7-a", "value"),
        Input("lattice-8-a", "value"),
        # b parameters
        Input("lattice-1-b", "value"),
        Input("lattice-2-b", "value"),
        Input("lattice-3-b", "value"),
        Input("lattice-4-b", "value"),
        Input("lattice-5-b", "value"),
        Input("lattice-6-b", "value"),
        Input("lattice-7-b", "value"),
        Input("lattice-8-b", "value"),
        # c parameters
        Input("lattice-1-c", "value"),
        Input("lattice-2-c", "value"),
        Input("lattice-3-c", "value"),
        Input("lattice-4-c", "value"),
        Input("lattice-5-c", "value"),
        Input("lattice-6-c", "value"),
        Input("lattice-7-c", "value"),
        Input("lattice-8-c", "value"),
        # alpha parameters
        Input("lattice-1-alpha", "value"),
        Input("lattice-2-alpha", "value"),
        Input("lattice-3-alpha", "value"),
        Input("lattice-4-alpha", "value"),
        Input("lattice-5-alpha", "value"),
        Input("lattice-6-alpha", "value"),
        Input("lattice-7-alpha", "value"),
        Input("lattice-8-alpha", "value"),
        # beta parameters
        Input("lattice-1-beta", "value"),
        Input("lattice-2-beta", "value"),
        Input("lattice-3-beta", "value"),
        Input("lattice-4-beta", "value"),
        Input("lattice-5-beta", "value"),
        Input("lattice-6-beta", "value"),
        Input("lattice-7-beta", "value"),
        Input("lattice-8-beta", "value"),
        # gamma parameters
        Input("lattice-1-gamma", "value"),
        Input("lattice-2-gamma", "value"),
        Input("lattice-3-gamma", "value"),
        Input("lattice-4-gamma", "value"),
        Input("lattice-5-gamma", "value"),
        Input("lattice-6-gamma", "value"),
        Input("lattice-7-gamma", "value"),
        Input("lattice-8-gamma", "value"),
        # Lattice scale sliders
        Input("lattice-scale-1", "value"),
        Input("lattice-scale-2", "value"),
        Input("lattice-scale-3", "value"),
        Input("lattice-scale-4", "value"),
        Input("lattice-scale-5", "value"),
        Input("lattice-scale-6", "value"),
        Input("lattice-scale-7", "value"),
        Input("lattice-scale-8", "value"),
        # Intensity sliders
        Input("intensity-1", "value"),
        Input("intensity-2", "value"),
        Input("intensity-3", "value"),
        Input("intensity-4", "value"),
        Input("intensity-5", "value"),
        Input("intensity-6", "value"),
        Input("intensity-7", "value"),
        Input("intensity-8", "value"),
        # Background sliders
        Input("background-1", "value"),
        Input("background-2", "value"),
        Input("background-3", "value"),
        Input("background-4", "value"),
        Input("background-5", "value"),
        Input("background-6", "value"),
        Input("background-7", "value"),
        Input("background-8", "value")
    ],
    State("cif-store", "data")
)
def update_xrd_plot(xy_data, opacity,
                    a1, a2, a3, a4, a5, a6, a7, a8,
                    b1, b2, b3, b4, b5, b6, b7, b8,
                    c1, c2, c3, c4, c5, c6, c7, c8,
                    alpha1, alpha2, alpha3, alpha4, alpha5, alpha6, alpha7, alpha8,
                    beta1, beta2, beta3, beta4, beta5, beta6, beta7, beta8,
                    gamma1, gamma2, gamma3, gamma4, gamma5, gamma6, gamma7, gamma8,
                    scale1, scale2, scale3, scale4, scale5, scale6, scale7, scale8,
                    intensity1, intensity2, intensity3, intensity4, intensity5, intensity6, intensity7, intensity8,
                    background1, background2, background3, background4, background5, background6, background7, background8,
                    cif_data):
    if cif_data is None:
        return {}
    patterns = []
    titles = []
    file_names = sorted(cif_data.keys())
    num_files = len(file_names)
    a_vals = [a1, a2, a3, a4, a5, a6, a7, a8]
    b_vals = [b1, b2, b3, b4, b5, b6, b7, b8]
    c_vals = [c1, c2, c3, c4, c5, c6, c7, c8]
    alpha_vals = [alpha1, alpha2, alpha3, alpha4, alpha5, alpha6, alpha7, alpha8]
    beta_vals = [beta1, beta2, beta3, beta4, beta5, beta6, beta7, beta8]
    gamma_vals = [gamma1, gamma2, gamma3, gamma4, gamma5, gamma6, gamma7, gamma8]
    scale_vals = [scale1, scale2, scale3, scale4, scale5, scale6, scale7, scale8]
    intensity_vals = [intensity1, intensity2, intensity3, intensity4, intensity5, intensity6, intensity7, intensity8]
    background_vals = [background1, background2, background3, background4, background5, background6, background7, background8]
    
    for i in range(num_files):
        file_name = file_names[i]
        try:
            structure = parse_cif(cif_data[file_name])
            structure = normalize_structure(structure)
        except Exception as e:
            print("Error parsing CIF for", file_name, ":", e)
            continue
        try:
            scale_factor = 1 + (scale_vals[i] / 100) if scale_vals[i] is not None else 1
            new_a = a_vals[i] * scale_factor
            new_b = b_vals[i] * scale_factor
            new_c = c_vals[i] * scale_factor
            new_alpha = alpha_vals[i]
            new_beta = beta_vals[i]
            new_gamma = gamma_vals[i]
            new_lattice = structure.lattice.from_parameters(new_a, new_b, new_c, new_alpha, new_beta, new_gamma)
            new_structure = Structure(new_lattice, structure.species, structure.frac_coords)
        except Exception as e:
            print("Error updating lattice for", file_name, ":", e)
            new_structure = structure

        calculator = XRDCalculator(wavelength="CuKa")
        try:
            pattern = calculator.get_pattern(new_structure, two_theta_range=(10, 120))
        except Exception as e:
            print("Error in XRD calculation for", file_name, ":", e)
            continue

        # Work on a fresh copy of the original intensities.
        orig_y = list(pattern.y)
        # Apply intensity scaling (per CIF)
        if intensity_vals[i] is not None and intensity_vals[i] != 100:
            scaled_y = [val * (intensity_vals[i] / 100) for val in orig_y]
        else:
            scaled_y = orig_y
        # Add the background offset (non-cumulatively)
        if background_vals[i] is not None and background_vals[i] > 0:
            new_y = [val + background_vals[i] for val in scaled_y]
        else:
            new_y = scaled_y
        pattern.y = new_y

        patterns.append(pattern)
        titles.append(file_name)
    
    exp_data = None
    if xy_data:
        try:
            parsed_data = json.loads(xy_data)
            exp_data = pd.DataFrame(parsed_data['data'], columns=parsed_data['columns'], index=parsed_data['index'])
        except ValueError as e:
            exp_data = None
    else:
        exp_data = None

    fig = plot_xrd(patterns, titles, "CuKa", experimental_data=exp_data, opacity=opacity)
    
    max_y_list = [max(pattern.y) for pattern in patterns if pattern.y is not None and len(pattern.y) > 0]
    max_y = max(max_y_list) if max_y_list else 100
    fig.update_layout(
        yaxis=dict(
            range=[0, max(105, max_y + 5)],
            dtick=10,
            gridcolor='lightgray',
            gridwidth=1
        )
    )
    return fig

# ------------------------------------------------------------------
# Download Link Callback
# ------------------------------------------------------------------
@app.callback(
    Output("download-link", "href"),
    Input("xrd-plot", "figure")
)
def update_download_link(figure):
    if not figure:
        return ""
    try:
        fig = go.Figure(figure)
        fig.update_layout(
            width=1800,
            height=400,
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(size=14),
            margin=dict(l=50, r=50, t=50, b=50),
            showlegend=True
        )
        pio.kaleido.scope.mathjax = None
        img_bytes = pio.to_image(
            fig,
            format="png",
            scale=2,
            engine="kaleido",
            width=1800,
            height=400,
            validate=False
        )
        b64_str = base64.b64encode(img_bytes).decode("ascii")
        href = f"data:image/png;base64,{b64_str}"
        return href
    except Exception as e:
        print("Error in generating download link:", e)
        return ""