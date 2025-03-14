from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    from .models.database import crear_tablas
    crear_tablas()
    
    from .routes.transacciones import transacciones_bp
    app.register_blueprint(transacciones_bp, url_prefix='/api/transacciones')

    from .routes.usuarios import usuarios_bp
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')

    return app