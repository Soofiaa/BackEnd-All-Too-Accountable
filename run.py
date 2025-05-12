from flask import Flask, send_from_directory
from flask_cors import CORS
from database import db
from app.extensions import mail
import os

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
from app.routes.chat_ia import chat_ia_bp
from app.routes.transacciones_completas import transacciones_completas_bp
from app.routes.gastos_mensuales import gastos_mensuales_bp

app = Flask(__name__)

# Activar CORS 
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Configuración base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:***REMOVED***@localhost/all_too_accountable'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'soofiaa.menzel@gmail.com'
app.config['MAIL_PASSWORD'] = '***REMOVED***'
app.config['MAIL_DEFAULT_SENDER'] = 'soofiaa.menzel@gmail.com'

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


'''
# PRUEBA PARA ENVIAR CORREOS
from email.mime.text import MIMEText
from smtplib import SMTP

@app.route('/probar_correo')
def probar_correo():
    try:
        mensaje = MIMEText("Hola, este es un correo de prueba", _charset="utf-8")
        mensaje["Subject"] = "Correo de prueba"
        mensaje["From"] = "soofiaa.menzel@gmail.com"
        mensaje["To"] = "soofiaa.menzel@gmail.com"

        # Conexión SMTP directa
        with SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login("soofiaa.menzel@gmail.com", "***REMOVED***")
            smtp.send_message(mensaje)

        return "✅ Correo enviado correctamente con UTF-8 forzado"
    except Exception as e:
        return f"❌ Error al enviar correo: {str(e)}"
'''