import os
import dash
from layout import create_layout
from callbacks import register_callbacks

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define WSGI-compatible server instance
server = app.server  

# Set up layout and callbacks
def initialize_app():
    try:
        app.layout = create_layout(app)
        register_callbacks(app)
    except Exception as e:
        print(f"Error initializing app: {e}")

initialize_app()

# Run the app in debug mode only when executed directly
if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run_server(debug=debug_mode)
