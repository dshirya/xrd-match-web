import dash

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define WSGI-compatible server instance
server = app.server