from flask import Blueprint, request, jsonify
from database import conectar_bd
import uuid
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import os

recuperar_contrasena_bp = Blueprint("recuperar_contrasena", __name__)

@recuperar_contrasena_bp.route("", methods=["POST"])
def recuperar_contrasena():
    data = request.get_json()
    correo = data.get("email", "").strip()

    # Validar que el correo esté presente y bien formateado
    import re
    if not correo or not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", correo):
        return jsonify({"error": "Correo inválido"}), 400

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        # Buscar usuario por correo
        cursor.execute("SELECT id_usuario, nombre_usuario FROM usuarios WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({"error": "Correo no encontrado"}), 404

        id_usuario = usuario["id_usuario"]
        nombre_usuario = usuario["nombre_usuario"]
        token = str(uuid.uuid4())
        expiracion = datetime.now() + timedelta(hours=1)

        # Insertar token de recuperación
        cursor.execute("""
            INSERT INTO tokens_recuperacion (id_usuario, token, fecha_expiracion)
            VALUES (%s, %s, %s)
        """, (id_usuario, token, expiracion))

        conexion.commit()
        cursor.close()
        conexion.close()

        # Enlace para el frontend
        link = f"http://localhost:5173/restablecer_contrasena?token={token}"

        cuerpo = f"""Hola {nombre_usuario},\n\nRecibimos una solicitud para restablecer tu contraseña.
        Haz clic en el siguiente enlace para continuar (válido por 1 hora):
        {link}

        Si no solicitaste esto, puedes ignorar este mensaje.

        Saludos,
        Equipo All Too Accountable
        """

        mail_username = os.getenv("MAIL_USERNAME")
        mail_password = os.getenv("MAIL_PASSWORD")

        msg = MIMEText(cuerpo, _charset="utf-8")
        msg['Subject'] = "Recuperación de contraseña - All Too Accountable"
        msg['From'] = mail_username
        msg['To'] = correo

        # Enviar correo
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(mail_username, mail_password)
            servidor.send_message(msg)
            print("Correo de recuperación enviado correctamente.")
            return jsonify({
                "mensaje": "Correo enviado correctamente",
                "token": token,
                "enlace": link
            }), 200

    except Exception as e:
        print(f"ERROR AL ENVIAR CORREO: {e}")
        return jsonify({
            "error": "No se pudo enviar el correo",
            "detalle": str(e)
        }), 500