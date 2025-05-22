from flask import Blueprint, request, jsonify
from app.models.usuario import Usuario
from app.utils.seguridad import verificar_password
from datetime import datetime
import re

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    correo = data.get('correo', '').strip()
    contrasena = data.get('contrasena', '')

    # Validar campos vacíos
    if not correo or not contrasena:
        return jsonify({"success": False, "message": "Correo y contraseña son obligatorios"}), 400

    # Validar formato del correo
    regex_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(regex_email, correo):
        return jsonify({"success": False, "message": "Correo inválido"}), 400

    # Buscar usuario
    usuario = Usuario.query.filter_by(correo=correo).first()

    # Validar contraseña
    if usuario and verificar_password(contrasena, usuario.contrasena):
        return jsonify({
            "mensaje": "Inicio de sesión exitoso",
            "usuario": {
                "id_usuario": usuario.id_usuario,
                "nombre_usuario": usuario.nombre_usuario
            }
        }), 200
    else:
        # Log interno de intento fallido
        print(f"[{datetime.now()}] Login fallido para: {correo}")
        return jsonify({"success": False, "message": "Correo o contraseña incorrectos"}), 401