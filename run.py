from flask import Flask
from flask_cors import CORS
from database import db
from app.extensions import mail

from app.routes.usuarios import usuarios_bp
from app.routes.login import login_bp
from app.routes.transacciones import transacciones_bp
from app.routes.categorias import categorias_bp

app = Flask(__name__)
CORS(app)

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

db.init_app(app)
mail.init_app(app)

# 🔧 Mueve los blueprints AQUÍ, después de definir `app`
app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")
app.register_blueprint(login_bp, url_prefix="/api/usuarios")
app.register_blueprint(transacciones_bp, url_prefix="/api/transacciones")
app.register_blueprint(categorias_bp, url_prefix="/api/categorias")

@app.route('/')
def index():
    return 'Backend All Too Accountable activo'

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