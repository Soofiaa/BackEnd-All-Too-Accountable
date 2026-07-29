from flask import Flask, send_from_directory
from flask_cors import CORS
from database import db
from app.extensions import mail
import os
from dotenv import load_dotenv

load_dotenv()

# Blueprints
from app.routes.usuarios import usuarios_bp
from app.routes.login import login_bp
from app.routes.categorias import categorias_bp
from app.routes.metas_ahorro import metas_ahorro_bp as metas_bp
from app.routes.recuperar_contrasena import recuperar_contrasena_bp
from app.routes.restablecer_contrasena import restablecer_contrasena_bp
from app.routes.transacciones import transacciones_bp
from app.routes.pagos_programados import gastos_programados_bp
from app.routes.detalles_usuarios import detalles_usuario_bp
from app.routes.ahorros import mov_ahorro_bp
from app.routes.DESCARTADOS.chat_ia import chat_ia_bp
from app.routes.transacciones_completas import transacciones_completas_bp
from app.routes.gastos_mensuales import gastos_mensuales_bp
from app.routes.importar_movimientos import importar_bp
from app.routes.ocr import ocr_bp
from app.routes.promedios import promedios_bp
from app.routes.estadisticas import estadisticas_bp
from app.routes.generar_transacciones import generar_transacciones_bp

app = Flask(__name__)

# Activar CORS 
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# Configuración base de datos
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

# Inicializar extensiones
db.init_app(app)
mail.init_app(app)

# Registrar blueprints
app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")
app.register_blueprint(login_bp, url_prefix="/api/usuarios")
app.register_blueprint(categorias_bp, url_prefix="/api/categorias")
app.register_blueprint(gastos_mensuales_bp, url_prefix="/api/gastos_mensuales")
app.register_blueprint(metas_bp, url_prefix="/api/metas")
app.register_blueprint(recuperar_contrasena_bp, url_prefix="/api/recuperar_contrasena")
app.register_blueprint(restablecer_contrasena_bp, url_prefix="/api/restablecer_contrasena")
app.register_blueprint(transacciones_bp, url_prefix="/api/transacciones")
app.register_blueprint(gastos_programados_bp, url_prefix="/api/pagos_programados")
app.register_blueprint(detalles_usuario_bp)
app.register_blueprint(mov_ahorro_bp, url_prefix="/api/movimientos_ahorro")
app.register_blueprint(chat_ia_bp, url_prefix="/api")
app.register_blueprint(transacciones_completas_bp)
app.register_blueprint(importar_bp)
app.register_blueprint(ocr_bp)
app.register_blueprint(promedios_bp, url_prefix="/api/promedios")
app.register_blueprint(estadisticas_bp, url_prefix="/api/estadisticas")
app.register_blueprint(generar_transacciones_bp)

@app.route('/')
def index():
    return 'Backend All Too Accountable activo'

# Servir archivos del directorio uploads
@app.route('/uploads/<path:filename>')
def descargar_archivo(filename):
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    return send_from_directory(uploads_dir, filename)

@app.route('/imagenes/<path:filename>')
def descargar_imagen(filename):
    imagenes_dir = os.path.join(os.getcwd(), 'imagenes_transacciones')
    return send_from_directory(imagenes_dir, filename)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)