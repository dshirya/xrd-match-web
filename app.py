from layout import app
import callbacks  

server = app.server  

if __name__ == "__main__":
    app.run(debug=True, port=8050)
