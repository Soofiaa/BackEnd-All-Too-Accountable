# routes/detalles_usuario.py

from flask import Blueprint, request, jsonify
from database import conectar_bd

detalles_usuario_bp = Blueprint('detalles_usuario', __name__)

@detalles_usuario_bp.route("/api/detalles_usuario", methods=["GET"])
def obtener_detalles_usuario():
    id_usuario = request.args.get("id_usuario")
    db = conectar_bd()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT salario, ahorros, dia_facturacion FROM detalles_usuario WHERE id_usuario = %s", (id_usuario,))
    detalles = cursor.fetchone()

    cursor.execute("SELECT nombre_usuario FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    usuario = cursor.fetchone()

    if detalles and usuario:
        return jsonify({**detalles, **usuario})
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404


@detalles_usuario_bp.route("/api/actualizar_salario", methods=["POST"])
def actualizar_salario():
    data = request.json
    id_usuario = data.get("id_usuario")
    nuevo_salario = data.get("salario")

    db = conectar_bd()
    cursor = db.cursor()
    cursor.execute("UPDATE detalles_usuario SET salario = %s WHERE id_usuario = %s", (nuevo_salario, id_usuario))
    db.commit()

    return jsonify({"mensaje": "Salario actualizado correctamente"})


@detalles_usuario_bp.route("/api/actualizar_ahorros", methods=["POST"])
def actualizar_ahorros():
    data = request.json
    id_usuario = data.get("id_usuario")
    nuevos_ahorros = data.get("ahorros")

    db = conectar_bd()
    cursor = db.cursor()
    cursor.execute("UPDATE detalles_usuario SET ahorros = %s WHERE id_usuario = %s", (nuevos_ahorros, id_usuario))
    db.commit()

    return jsonify({"mensaje": "Ahorros actualizados correctamente"})

@detalles_usuario_bp.route("/api/actualizar_nombre", methods=["POST"])
def actualizar_nombre_usuario():
    data = request.json
    id_usuario = data.get("id_usuario")
    nuevo_nombre = data.get("nombre_usuario")

    db = conectar_bd()
    cursor = db.cursor()
    cursor.execute("UPDATE usuarios SET nombre_usuario = %s WHERE id_usuario = %s", (nuevo_nombre, id_usuario))
    db.commit()

    return jsonify({"mensaje": "Nombre actualizado correctamente"})

@detalles_usuario_bp.route("/api/actualizar_facturacion", methods=["POST"])
def actualizar_dia_facturacion():
    data = request.json
    id_usuario = data.get("id_usuario")
    dia_facturacion = data.get("dia_facturacion")

    db = conectar_bd()
    cursor = db.cursor()
    cursor.execute("UPDATE detalles_usuario SET dia_facturacion = %s WHERE id_usuario = %s", (dia_facturacion, id_usuario))
    db.commit()

    return jsonify({"mensaje": "Día de facturación actualizado correctamente"})
