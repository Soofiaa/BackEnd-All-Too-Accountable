from flask import Blueprint, request, jsonify
from database import db
from app.models.usuario import Usuario
from app.utils.seguridad import hash_password
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

usuarios_bp = Blueprint('usuarios', __name__)

def enviar_correo(destinatario, nombre_usuario):
    cuerpo = (
        f"Hola {nombre_usuario}, gracias por crear tu cuenta en All Too Accountable.\n"
        "Tu cuenta ha sido creada con exito."
    )

    msg = MIMEText(cuerpo, _charset="utf-8")
    msg['Subject'] = "Registro exitoso en All Too Accountable"
    msg['From'] = "soofiaa.menzel@gmail.com"
    msg['To'] = destinatario

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login("soofiaa.menzel@gmail.com", "llio ocef kspn nlzj")  # clave app Gmail
            servidor.send_message(msg)
            print("✅ Correo enviado correctamente.")
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")

@usuarios_bp.route('/registro', methods=['POST'])
def registrar_usuario():
    datos = request.json
    nombre_usuario = datos.get('nombre_usuario')
    correo = datos.get('correo')
    contrasena = datos.get('contrasena')
    fecha_nacimiento = datos.get('fecha_nacimiento')
    
    # Validar edad mínima
    try:
        fecha_nac_dt = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        hoy = datetime.today()
        edad = hoy.year - fecha_nac_dt.year - ((hoy.month, hoy.day) < (fecha_nac_dt.month, fecha_nac_dt.day))

        if edad < 13:
            return jsonify({"error": "Debes tener al menos 13 años para registrarte."}), 403
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}), 400

    if not all([nombre_usuario, correo, contrasena, fecha_nacimiento]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({"error": "El correo ya esta registrado"}), 409

    usuario = Usuario(
        nombre_usuario=nombre_usuario,
        correo=correo,
        contrasena=hash_password(contrasena),
        fecha_nacimiento=fecha_nacimiento
    )
    db.session.add(usuario)
    db.session.commit()

    # Enviar correo de bienvenida sin errores de codificación
    enviar_correo(correo, nombre_usuario)

    return jsonify({"mensaje": "Usuario registrado correctamente"}), 201