from flask import Blueprint, request, jsonify
from database import db
from app.models.usuario import Usuario
from app.utils.seguridad import hash_password
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from app.models.usuario import Usuario
from database import conectar_bd
import os


usuarios_bp = Blueprint('usuarios', __name__)

def enviar_correo(destinatario, nombre_usuario):
    cuerpo = (
        f"Hola {nombre_usuario}, gracias por crear tu cuenta en All Too Accountable.\n"
        "Tu cuenta ha sido creada con exito."
    )

    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")

    msg = MIMEText(cuerpo, _charset="utf-8")
    msg['Subject'] = "Registro exitoso en All Too Accountable"
    msg['From'] = mail_username
    msg['To'] = destinatario

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(mail_username, mail_password)
            servidor.send_message(msg)
            print("Correo enviado correctamente.")
    except Exception as e:
        print(f"Error al enviar correo: {e}")


@usuarios_bp.route('/registro', methods=['POST'])
def registrar_usuario():
    datos = request.get_json()

    nombre_usuario = datos.get('nombre_usuario', '').strip()
    correo = datos.get('correo', '').strip()
    contrasena = datos.get('contrasena', '')
    fecha_nacimiento = datos.get('fecha_nacimiento')

    import re

    # Validar campos vacíos
    if not all([nombre_usuario, correo, contrasena, fecha_nacimiento]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    # Validar nombre
    if len(nombre_usuario) < 2 or len(nombre_usuario) > 100:
        return jsonify({"error": "Nombre de usuario inválido"}), 400

    # Validar correo con formato correcto
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", correo):
        return jsonify({"error": "Correo inválido"}), 400

    # Validar contraseña segura
    if len(contrasena) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    # Validar edad
    try:
        fecha_nac_dt = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        hoy = datetime.today()
        edad = hoy.year - fecha_nac_dt.year - ((hoy.month, hoy.day) < (fecha_nac_dt.month, fecha_nac_dt.day))
        if edad < 13:
            return jsonify({"error": "Debes tener al menos 13 años para registrarte."}), 403
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}), 400

    # Validar si el correo ya existe
    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({"error": "El correo ya está registrado"}), 409

    # Crear usuario
    usuario = Usuario(
        nombre_usuario=nombre_usuario,
        correo=correo,
        contrasena=hash_password(contrasena),
        fecha_nacimiento=fecha_nacimiento
    )
    db.session.add(usuario)
    db.session.commit()

    enviar_correo(correo, nombre_usuario)

    return jsonify({"mensaje": "Usuario registrado correctamente"}), 201


@usuarios_bp.route('/<int:id_usuario>', methods=['GET'])
def obtener_usuario(id_usuario):
    try:
        db = conectar_bd()
        cursor = db.cursor()
        cursor.execute("SELECT nombre_usuario FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        resultado = cursor.fetchone()
        db.close()

        if resultado:
            return jsonify({"nombre_usuario": resultado["nombre_usuario"]})
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
