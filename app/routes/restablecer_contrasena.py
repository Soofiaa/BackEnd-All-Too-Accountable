from flask import Blueprint, request, jsonify
from app.utils.seguridad import hash_password
from database import conectar_bd
import bcrypt
import datetime
import traceback
import bcrypt
from pymysql.cursors import DictCursor


restablecer_contrasena_bp = Blueprint('restablecer_contrasena', __name__)

@restablecer_contrasena_bp.route('', methods=['POST'])
def restablecer_contrasena():
    try:
        data = request.get_json()
        token = data.get("token")
        nueva_contrasena = data.get("nueva_contrasena")

        if not token or not nueva_contrasena:
            return jsonify({"error": "Faltan datos requeridos"}), 400

        conn = conectar_bd()
        cursor = conn.cursor(DictCursor)

        # Verificar si el token existe
        cursor.execute("SELECT id_usuario FROM tokens_recuperacion WHERE token = %s", (token,))
        resultado = cursor.fetchone()
        if not resultado:
            return jsonify({"error": "Token inválido o expirado"}), 400

        id_usuario = resultado["id_usuario"]

        nueva_contrasena_encriptada = hash_password(nueva_contrasena)

        # Actualizar la contraseña del usuario
        cursor.execute("UPDATE usuarios SET contrasena = %s WHERE id_usuario = %s",
                        (nueva_contrasena_encriptada, id_usuario))

        # Eliminar el token usado
        cursor.execute("DELETE FROM tokens_recuperacion WHERE token = %s", (token,))
        conn.commit()

        return jsonify({"mensaje": "Contraseña actualizada correctamente"}), 200

    except Exception as e:
        import traceback
        print("❌ ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor"}), 500