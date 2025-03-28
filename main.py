import callbacks  
from layout import create_layout
from callbacks import register_callbacks
import dash
import os

# Initialize Dash app
app = dash.Dash(__name__)

# Define WSGI-compatible server instance
server = app.server  

# Set up layout and callbacks
try:
    app.layout = create_layout(app)
    register_callbacks(app)
except Exception as e:
    print(f"Error initializing app: {e}")

# Run the app in debug mode only when executed directly
if __name__ == '__main__':
    app.run_server(debug=os.getenv('DEBUG', 'False').lower() == 'true')
