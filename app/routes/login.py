from flask import Blueprint, request, jsonify
from app.models.usuario import Usuario
from app.utils.seguridad import verificar_password

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"success": False, "message": "Correo y contraseña requeridos"}), 400

    usuario = Usuario.query.filter_by(correo=email).first()

    if not usuario or not verificar_password(password, usuario.contrasena):
        return jsonify({"success": False, "message": "Credenciales inválidas"}), 401

    return jsonify({
        "success": True,
        "message": "Inicio de sesión exitoso",
        "usuario": {
            "id": usuario.id,
            "nombre_usuario": usuario.nombre_usuario,
            "correo": usuario.correo
        }
    }), 200
