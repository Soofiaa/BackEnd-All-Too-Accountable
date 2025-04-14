from flask import Blueprint, request, jsonify
from database import conectar_bd
import uuid
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

recuperar_contrasena_bp = Blueprint("recuperar_contrasena", __name__)

@recuperar_contrasena_bp.route("", methods=["POST"])
def recuperar_contrasena():
    data = request.get_json()
    correo = data.get("email")

    if not correo:
        return jsonify({"error": "Correo requerido"}), 400

    conexion = conectar_bd()
    cursor = conexion.cursor()

    # Buscar usuario
    cursor.execute("SELECT id_usuario, nombre_usuario FROM usuarios WHERE correo = %s", (correo,))
    usuario = cursor.fetchone()

    if not usuario:
        return jsonify({"error": "Correo no encontrado"}), 404

    id_usuario = usuario["id_usuario"]
    nombre_usuario = usuario["nombre_usuario"]
    token = str(uuid.uuid4())
    expiracion = datetime.now() + timedelta(hours=1)

    # Insertar token
    cursor.execute("""
        INSERT INTO tokens_recuperacion (id_usuario, token, fecha_expiracion)
        VALUES (%s, %s, %s)
    """, (id_usuario, token, expiracion))

    conexion.commit()
    cursor.close()
    conexion.close()

    # Construir enlace y cuerpo del correo
    link = f"http://localhost:5173/restablecer_contrasena?token={token}"
    cuerpo = f"""Hola {nombre_usuario},\n\nRecibimos una solicitud para restablecer tu contraseña.
    Haz clic en el siguiente enlace para continuar (válido por 1 hora):
    {link}

    Si no solicitaste esto, puedes ignorar este mensaje.

    Saludos,
    Equipo All Too Accountable
    """

    msg = MIMEText(cuerpo, _charset="utf-8")
    msg['Subject'] = "Recuperacion de contrasena - All Too Accountable"
    msg['From'] = "soofiaa.menzel@gmail.com"
    msg['To'] = correo

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login("soofiaa.menzel@gmail.com", "llio ocef kspn nlzj")  # clave app Gmail
            servidor.send_message(msg)
            print("✅ Correo de recuperación enviado correctamente.")
            return jsonify({"mensaje": "Correo enviado correctamente", "token": token, "enlace": link}), 200
    except Exception as e:
        print(f"❌ ERROR AL ENVIAR CORREO: {e}")
        return jsonify({"error": "No se pudo enviar el correo", "detalle": str(e)}), 500
