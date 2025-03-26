import math
import plotly.graph_objects as go

def plot_xrd(patterns, titles, wavelength, experimental_data=None, opacity=0.9):
    """
    Generate a Plotly figure of XRD patterns.
    
    :param patterns: List of XRD pattern objects. Each pattern should provide angle and intensity data,
                     either as attributes (pattern.x, pattern.y) or as a two-column iterable.
    :param titles: List of titles (one for each pattern).
    :param wavelength: The radiation type (string) used.
    :param experimental_data: (Optional) Pandas DataFrame with '2_theta' and 'intensity' columns.
    :param opacity: Opacity of the pattern bars.
    """
    
    def extract_xy(pattern):
        # Attempt to retrieve x and y as attributes; otherwise assume two-column data.
        try:
            return pattern.x, pattern.y
        except AttributeError:
            x_vals = [row[0] for row in pattern]
            y_vals = [row[1] for row in pattern]
            return x_vals, y_vals

    fig = go.Figure()

    # Determine the x-axis range.
    if experimental_data is not None:
        x_min = experimental_data['2_theta'].min()
        x_max = experimental_data['2_theta'].max()
        fig.add_trace(go.Scatter(
            x=experimental_data['2_theta'], 
            y=experimental_data['intensity'],
            mode='lines', 
            name='Experimental Data',
            line=dict(color='black', width=1)
        ))
    else:
        # Compute x_min and x_max from all provided patterns.
        x_min = min(min(extract_xy(pattern)[0]) for pattern in patterns)
        x_max = max(max(extract_xy(pattern)[0]) for pattern in patterns)
    
    # Add each pattern as a Bar trace (only data within the computed range).
    for pattern, title in zip(patterns, titles):
        x_vals, y_vals = extract_xy(pattern)
        valid_indices = [i for i, x_val in enumerate(x_vals) if x_min <= x_val <= x_max]
        fig.add_trace(go.Bar(
            x=[x_vals[i] for i in valid_indices],
            y=[y_vals[i] for i in valid_indices],
            name=title,
            width=0.15,
            opacity=opacity
        ))
    
    # Determine integer bounds for tick marks.
    x_lower = int(math.floor(x_min))
    x_upper = int(math.ceil(x_max))
    
    # Prepare built-in tick labels (only for multiples of 10) as integers.
    big_ticks = [x for x in range(x_lower, x_upper + 1) if x % 10 == 0]
    
    # Create custom tick mark shapes.
    tick_shapes = []
    for x in range(x_lower, x_upper + 1):
        if x % 10 == 0:
            # Big tick: every 10°
            tick_length = 0.04  # in paper coordinates (relative height)
            tick_color = 'black'
            tick_width = 2
        elif x % 5 == 0:
            # Medium tick: every 5° (not multiple of 10)
            tick_length = 0.03
            tick_color = 'grey'
            tick_width = 1.5
        else:
            # Small tick: every 1° (that are not multiples of 5)
            tick_length = 0.02
            tick_color = 'grey'
            tick_width = 1
        tick_shapes.append(
            dict(
                type="line",
                xref="x", yref="paper",
                x0=x, x1=x,
                y0=0, y1=tick_length,
                line=dict(color=tick_color, width=tick_width)
            )
        )
    
    # Update layout with custom x-axis tick labels and custom tick shapes.
    fig.update_layout(
        title=dict(
            text=f"XRD Patterns (Wavelength: {wavelength})",
            font=dict(family="Dejavu Sans", size=41)
        ),
        font=dict(family="Dejavu Sans", size=27),
        xaxis=dict(
            title=dict(text="2θ (degrees)", font=dict(family="Dejavu Sans", size=27)),
            range=[x_min, x_max],
            tickmode='array',
            tickvals=big_ticks,
            ticktext=[str(t) for t in big_ticks],
            ticks="",  # Disable default tick marks; custom shapes are used instead.
            gridcolor='lightgray',
            gridwidth=1,
            zeroline=False
        ),
        yaxis=dict(
            title=dict(text="Intensity", font=dict(family="Dejavu Sans", size=27)),
            range=[0, 105],
            gridcolor='lightgray',
            gridwidth=1,
            tickfont=dict(family="Dejavu Sans", size=27)
        ),
        shapes=tick_shapes,
        template="plotly_white",
        barmode='overlay',
        plot_bgcolor='white'
    )
    
    return fig