from flask import Blueprint, request, jsonify
from app.models.usuario import Usuario
from app.utils.seguridad import verificar_password

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    correo = data.get('correo')
    contrasena = data.get('contrasena')

    if not correo or not contrasena:
        return jsonify({"success": False, "message": "Correo y contraseña son obligatorios"}), 400

    usuario = Usuario.query.filter_by(correo=correo).first()

    if usuario and verificar_password(contrasena, usuario.contrasena):
        return jsonify({
    "mensaje": "Inicio de sesión exitoso",
    "usuario": {
        "id_usuario": usuario.id_usuario,
        "nombre_usuario": usuario.nombre_usuario
    }
        }), 200
    else:
        return jsonify({"success": False, "message": "Correo o contraseña incorrectos"}), 401
