from dash import Dash
from layout import get_layout
from callbacks import register_callbacks

# Initialize the Dash app here.
app = Dash(__name__)
server = app.server

# Set the layout from layout.py.
app.layout = get_layout()

# Register all callbacks using the app instance.
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, port=8050)