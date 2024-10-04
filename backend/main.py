from flask import Flask
from routes.routes import api_blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS allows cross-origin requests

# Register API routes
app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    app.run(port=3000, debug=True)