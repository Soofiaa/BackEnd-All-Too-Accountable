from flask import Flask
from flask_cors import CORS
from app.routes.usuarios import usuarios_bp
from app.routes.login import login_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(usuarios_bp)
app.register_blueprint(login_bp)

if __name__ == "__main__":
    app.run(debug=True)
