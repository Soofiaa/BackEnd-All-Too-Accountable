from flask import Blueprint, request, jsonify
import sqlite3

usuarios_bp = Blueprint('usuarios', __name__)

DB_NAME = "alltooaccountable.db"

@usuarios_bp.route('/registro', methods=['POST'])
def registrar_usuario():
    datos = request.json
    nombre_usuario = datos.get('nombre_usuario')
    correo = datos.get('correo')
    contrasena = datos.get('contrasena')
    fecha_nacimiento = datos.get('fecha_nacimiento')

    if not all([nombre_usuario, correo, contrasena, fecha_nacimiento]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO usuarios (nombre_usuario, correo, contrasena, fecha_nacimiento)
            VALUES (?, ?, ?, ?)
        """, (nombre_usuario, correo, contrasena, fecha_nacimiento))

        conexion.commit()
        conexion.close()

        return jsonify({"mensaje": "Usuario registrado correctamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@usuarios_bp.route('/ping', methods=['GET'])
def ping_usuarios():
    return jsonify({"mensaje": "usuarios OK"})
