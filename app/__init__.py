from flask import Flask
from flask_cors import CORS
from database import db

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:prueba123@localhost/all_too_accountable'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    db.init_app(app)

    from database import crear_tablas
    crear_tablas()

    from .routes.usuarios import usuarios_bp
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')

    from .routes.login import login_bp
    app.register_blueprint(login_bp, url_prefix='/api/usuarios')

    from .routes.categorias import categorias_bp
    app.register_blueprint(categorias_bp, url_prefix="/api/categorias")
    
    from .routes.gastos_mensuales import gastos_mensuales_bp
    app.register_blueprint(gastos_mensuales_bp, url_prefix='/api/gastos')
    
    from .routes.metas_ahorro import metas_ahorro_bp
    app.register_blueprint(metas_ahorro_bp, url_prefix='/api/metas')

    db.create_all()

    return app