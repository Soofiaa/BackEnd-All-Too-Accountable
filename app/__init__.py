from flask import Flask
from flask_cors import CORS
from database import db

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:***REMOVED***@localhost/all_too_accountable'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    db.init_app(app)

    from database import crear_tablas
    crear_tablas()

    from .routes.usuarios import usuarios_bp
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')

    from .routes.login import login_bp
    app.register_blueprint(login_bp, url_prefix='/api/login')

    from .routes.categorias import categorias_bp
    app.register_blueprint(categorias_bp, url_prefix="/api/categorias")
    
    from .routes.gastos_mensuales import gastos_mensuales_bp
    app.register_blueprint(gastos_mensuales_bp, url_prefix='/api/gastos')
    
    from .routes.metas_ahorro import metas_ahorro_bp
    app.register_blueprint(metas_ahorro_bp, url_prefix='/api/metas')
    
    from .routes.recuperar_contrasena import recuperar_contrasena_bp
    app.register_blueprint(recuperar_contrasena_bp, url_prefix='/api/recuperar_contrasena')
    
    from .routes.restablecer_contrasena import restablecer_contrasena_bp
    app.register_blueprint(restablecer_contrasena_bp, url_prefix='/api/restablecer_contrasena')
    
    from .routes.transacciones import transacciones_bp
    app.register_blueprint(transacciones_bp, url_prefix='/api/transacciones')
    
    from .routes.pagos_pendientes import pagos_pendientes_bp
    app.register_blueprint(pagos_pendientes_bp, url_prefix='/api/pagos-pendientes')
    
    from .routes.detalles_usuarios import detalles_usuario_bp
    app.register_blueprint(detalles_usuario_bp, url_prefix='/api/detalles_usuario')

    from .routes.ahorros import mov_ahorro_bp
    app.register_blueprint(mov_ahorro_bp, url_prefix="/api/movimientos_ahorro")
    
    from app.routes.chat_ia import chat_ia_bp
    app.register_blueprint(chat_ia_bp, url_prefix="/api")

    db.create_all()

    return app