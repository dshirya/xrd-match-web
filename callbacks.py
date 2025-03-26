import base64
import pandas as pd
from dash import Input, Output, State, callback_context, no_update
import plotly.graph_objects as go
from layout import app
from preprocess import parse_xy, parse_cif, normalize_structure, XRDCalculator
from plot import plot_xrd
from pymatgen.core import Structure

# ------------------------------------------------------------------
# Check Mark Callbacks for File Uploads
# ------------------------------------------------------------------

# Update the .xy file upload check mark.
@app.callback(
    Output("xy-upload-status", "children"),
    Input("upload-xy", "contents")
)
def update_xy_status(contents):
    if contents:
        return "✓"
    return ""

# Update the .cif file upload check mark.
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

# Callback to store the uploaded .xy file in a dcc.Store.
@app.callback(
    Output("xy-store", "data"),
    Input("upload-xy", "contents"),
    State("upload-xy", "filename")
)
def store_xy_file(contents, filename):
    if contents is not None:
        try:
            df = parse_xy(contents)
            # Normalize intensity so that the maximum equals 100.
            max_intensity = df['intensity'].max()
            df['intensity'] = (df['intensity'] / max_intensity) * 100
            return df.to_json(date_format='iso', orient='split')
        except Exception as e:
            print("Error processing XY file:", e)
            return no_update
    return no_update

# Callback to store the uploaded CIF files in a dcc.Store.
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
                cif_data[name] = contents  # Save the base64 content string.
            except Exception as e:
                print("Error processing CIF file:", e)
        return cif_data
    return no_update

# ------------------------------------------------------------------
# Update Dropdown and Lattice Parameter Callbacks
# ------------------------------------------------------------------

# Callback to update the CIF dropdown based on stored CIF files.
@app.callback(
    Output("cif-selector", "options"),
    Output("cif-selector", "value"),
    Input("cif-store", "data")
)
def update_cif_dropdown(cif_data):
    if cif_data is None:
        return [], None
    options = [{"label": name, "value": name} for name in cif_data.keys()]
    first_value = options[0]["value"] if options else None
    return options, first_value

# Callback to update lattice parameter inputs when a CIF file is selected or the lattice scale changes.
@app.callback(
    [Output("a-input", "value"),
     Output("b-input", "value"),
     Output("c-input", "value"),
     Output("alpha-input", "value"),
     Output("beta-input", "value"),
     Output("gamma-input", "value"),
     Output("lattice-scale-slider", "value")],
    [Input("cif-selector", "value"),
     Input("lattice-scale-slider", "value")],
    State("cif-store", "data")
)
def update_lattice_parameters(selected_cif, scale_value, cif_data):
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    if not selected_cif or cif_data is None:
        return no_update, no_update, no_update, no_update, no_update, no_update, 0
    try:
        structure = parse_cif(cif_data[selected_cif])
        structure = normalize_structure(structure)
    except Exception as e:
        print("Error parsing CIF in update_lattice_parameters:", e)
        return no_update, no_update, no_update, no_update, no_update, no_update, 0
    lattice = structure.lattice
    if trigger_id == "cif-selector":
        return lattice.a, lattice.b, lattice.c, lattice.alpha, lattice.beta, lattice.gamma, 0
    elif trigger_id == "lattice-scale-slider":
        scale_factor = 1 + (scale_value / 100) if scale_value is not None else 1
        return (lattice.a * scale_factor, lattice.b * scale_factor, lattice.c * scale_factor,
                lattice.alpha, lattice.beta, lattice.gamma, scale_value)
    return lattice.a, lattice.b, lattice.c, lattice.alpha, lattice.beta, lattice.gamma, scale_value or 0

# ------------------------------------------------------------------
# XRD Plot, Download Link, and CIF Summary Callbacks
# ------------------------------------------------------------------

# Callback to update the XRD plot.
@app.callback(
    Output("xrd-plot", "figure"),
    [Input("cif-selector", "value"),
     Input("a-input", "value"),
     Input("b-input", "value"),
     Input("c-input", "value"),
     Input("alpha-input", "value"),
     Input("beta-input", "value"),
     Input("gamma-input", "value"),
     Input("scaling-input", "value"),
     Input("background-input", "value"),
     Input("opacity-slider", "value"),
     Input("xy-store", "data")],
    State("cif-store", "data")
)
def update_xrd_plot(selected_cif, a, b, c, alpha, beta, gamma, scaling, background, opacity, xy_data, cif_data):
    if not selected_cif or cif_data is None:
        return {}
    try:
        # Parse the selected CIF file.
        structure = parse_cif(cif_data[selected_cif])
        structure = normalize_structure(structure)
        # Create a new lattice using the updated parameters.
        new_lattice = structure.lattice.from_parameters(
            a or structure.lattice.a,
            b or structure.lattice.b,
            c or structure.lattice.c,
            alpha or structure.lattice.alpha,
            beta or structure.lattice.beta,
            gamma or structure.lattice.gamma
        )
        new_structure = Structure(new_lattice, structure.species, structure.frac_coords)
    except Exception as e:
        print("Error in update_xrd_plot while parsing structure:", e)
        return {}

    # Calculate the XRD pattern.
    calculator = XRDCalculator(wavelength="CuKa")
    try:
        pattern = calculator.get_pattern(new_structure, two_theta_range=(10, 120))
    except Exception as e:
        print("Error in XRD calculation:", e)
        return {}

    # Apply intensity scaling.
    if scaling is not None and scaling != 100:
        pattern.y = [val * (scaling / 100) for val in pattern.y]

    # Add background level.
    if background is not None and background > 0:
        pattern.y = [val + background for val in pattern.y]

    # Read experimental data if provided.
    exp_data = None
    if xy_data is not None:
        exp_data = pd.read_json(xy_data, orient='split')

    # Generate the figure.
    fig = plot_xrd([pattern], [selected_cif], "CuKa", experimental_data=exp_data, opacity=opacity)
    max_y = max(pattern.y) if len(pattern.y) > 0 else 100
    fig.update_layout(
        yaxis=dict(
            range=[0, max(105, max_y + 5)],
            dtick=10,
            gridcolor='lightgray',
            gridwidth=1
        )
    )
    return fig

# Callback to update the download link.
@app.callback(
    Output("download-link", "href"),
    Input("xrd-plot", "figure")
)
def update_download_link(figure):
    if not figure:
        return ""
    try:
        import plotly.io as pio
        fig = go.Figure(figure)
        fig.update_layout(
            width=1200,
            height=800,
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
            width=1200,
            height=800,
            validate=False
        )
        b64_str = base64.b64encode(img_bytes).decode("ascii")
        href = f"data:image/png;base64,{b64_str}"
        return href
    except Exception as e:
        print("Error in generating download link:", e)
        return ""

# Callback to display the CIF summary.
@app.callback(
    Output("cif-summary", "children"),
    Input("show-summary-button", "n_clicks"),
    State("cif-selector", "value"),
    State("cif-store", "data")
)
def show_cif_summary(n_clicks, selected_cif, cif_data):
    if not selected_cif or n_clicks == 0 or cif_data is None:
        return ""
    try:
        structure = parse_cif(cif_data[selected_cif])
        structure = normalize_structure(structure)
    except Exception as e:
        print("Error in showing CIF summary:", e)
        return "Error parsing CIF file."
    summary = f"Summary for {selected_cif}:\n\n"
    summary += f"Formula: {structure.composition.reduced_formula}\n"
    sg, num = structure.get_space_group_info()
    summary += f"Space Group: {sg} ({num})\n"
    summary += "Lattice Parameters:\n"
    summary += f"  a = {structure.lattice.a:.4f} Å\n"
    summary += f"  b = {structure.lattice.b:.4f} Å\n"
    summary += f"  c = {structure.lattice.c:.4f} Å\n"
    summary += f"  α = {structure.lattice.alpha:.4f}°\n"
    summary += f"  β = {structure.lattice.beta:.4f}°\n"
    summary += f"  γ = {structure.lattice.gamma:.4f}°\n"
    summary += f"Volume: {structure.volume:.4f} Å³\n"
    summary += f"Number of sites: {len(structure)}\n"
    return summary