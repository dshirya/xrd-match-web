import plotly.graph_objects as go

def plot_xrd(patterns, titles, wavelength, experimental_data=None, opacity=0.9):
    """
    Generate a Plotly figure of XRD patterns.
    :param patterns: List of XRD pattern objects (with .x and .y attributes).
    :param titles: List of titles (one for each pattern).
    :param wavelength: The radiation type (string) used.
    :param experimental_data: (Optional) Pandas DataFrame for experimental data.
    :param opacity: Opacity of the pattern bars.
    """
    fig = go.Figure()
    
    # Set default x-range.
    x_min, x_max = 10, 120
    
    # If experimental data is provided, adjust x-range and add it to the plot.
    if experimental_data is not None:
        exp_min = max(10, experimental_data['2_theta'].min())
        exp_max = min(120, experimental_data['2_theta'].max())
        x_min = exp_min
        x_max = exp_max
        
        fig.add_trace(go.Scatter(
            x=experimental_data['2_theta'], 
            y=experimental_data['intensity'],
            mode='lines', 
            name='Experimental Data',
            line=dict(color='black', width=1)
        ))
    
    # Add pattern traces.
    for pattern, title in zip(patterns, titles):
        valid_indices = [i for i, x_val in enumerate(pattern.x) if 10 <= x_val <= 120]
        fig.add_trace(go.Bar(
            x=[pattern.x[i] for i in valid_indices],
            y=[pattern.y[i] for i in valid_indices],
            name=title,
            width=0.15,
            opacity=opacity
        ))
    
    # Configure axes and grid.
    major_ticks = list(range(int(x_min) - int(x_min) % 10, int(x_max) + 11, 10))
    minor_ticks = list(range(int(x_min), int(x_max) + 1))
    
    fig.update_layout(
        title=f"XRD Patterns (Wavelength: {wavelength})",
        xaxis=dict(
            title="2θ (degrees)",
            range=[x_min, x_max],
            tickmode='array',
            tickvals=major_ticks,
            ticktext=[str(x) for x in major_ticks],
            gridcolor='lightgray',
            gridwidth=1,
            zeroline=False
        ),
        yaxis=dict(
            title="Intensity",
            range=[0, 105],
            dtick=10,
            gridcolor='lightgray',
            gridwidth=1
        ),
        template="plotly_white",
        barmode='overlay',
        plot_bgcolor='white'
    )
    
    return fig