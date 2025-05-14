import math
import plotly.graph_objects as go
import plotly.io as pio

def plot_xrd(patterns, titles, wavelength, experimental_data=None, opacity=0.9):
    """
    Generate a Plotly figure of XRD patterns.
    """
    
    def extract_xy(pattern):
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
            name='Experimental data',
            line=dict(color='black', width=1)
        ))
    else:
        x_min = min(min(extract_xy(pattern)[0]) for pattern in patterns)
        x_max = max(max(extract_xy(pattern)[0]) for pattern in patterns)

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

    x_lower = int(math.floor(x_min))
    x_upper = int(math.ceil(x_max))
    big_ticks = [x for x in range(x_lower, x_upper + 1) if x % 10 == 0]

    tick_shapes = []
    for x in range(x_lower, x_upper + 1):
        if x % 10 == 0:
            tick_length = 0.04
            tick_color = 'black'
            tick_width = 2
        elif x % 5 == 0:
            tick_length = 0.03
            tick_color = 'grey'
            tick_width = 1.5
        else:
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

    # Explicitly set the font to "Microsoft Sans Serif" and apply it throughout
    fig.update_layout(
        title=dict(
            text=f"XRD patterns (wavelength: {wavelength})",
            font=dict(family="Microsoft Sans Serif", size=30, color="black")
        ),
        font=dict(family="Microsoft Sans Serif", size=24, color="black"),
        xaxis=dict(
            title=dict(text="diffraction angle, 2<i>θ</i>", font=dict(family="Microsoft Sans Serif", size=24)),
            range=[x_min, x_max],
            tickmode='array',
            tickvals=big_ticks,
            ticktext=[str(t) for t in big_ticks],
            ticks="",
            gridcolor='lightgray',
            gridwidth=1,
            zeroline=False
        ),
        yaxis=dict(
            title=dict(text="intensity, a.u.", font=dict(family="Microsoft Sans Serif", size=24)),
            range=[0, 105],
            gridcolor='lightgray',
            gridwidth=1,
            tickfont=dict(family="Microsoft Sans Serif", size=24)
        ),
        shapes=tick_shapes,
        template="plotly_white",
        barmode='overlay',
        plot_bgcolor='white'
    )

    # Save the plot as an image using Kaleido engine without `config` argument
    pio.write_image(fig, 'xrd_pattern.png', engine="kaleido")
    
    return fig
