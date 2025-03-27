from flask import Blueprint, request, jsonify
import sqlite3
import hashlib

login_bp = Blueprint('login', __name__)
DB_NAME = "alltooaccountable.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"success": False, "message": "Correo y contraseña requeridos"}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM usuarios WHERE correo = ? AND contrasena = ?',
        (email, hashed_password)
    ).fetchone()
    conn.close()

    if user:
        return jsonify({"success": True, "message": "Inicio de sesión exitoso", "usuario": dict(user)})
    else:
        return jsonify({"success": False, "message": "Credenciales inválidas"}), 401
