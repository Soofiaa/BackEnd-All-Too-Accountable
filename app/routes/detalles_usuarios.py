# routes/detalles_usuario.py

from flask import Blueprint, request, jsonify
from database import conectar_bd
from app.models.ahorro import MovimientoAhorro

detalles_usuario_bp = Blueprint('detalles_usuario', __name__)

from app.models.detalle_usuario import DetallesUsuario


@detalles_usuario_bp.route('/api/detalles_usuario', methods=['GET'])
def obtener_detalles_usuario():
    id_usuario = request.args.get('id_usuario')
    detalles = DetallesUsuario.obtener_por_id(id_usuario)
    if detalles:
        return jsonify(detalles)
    else:
        return jsonify({"error": "Detalles no encontrados"}), 404


@detalles_usuario_bp.route("/api/actualizar_salario", methods=["POST"])
def actualizar_salario():
    data = request.json
    id_usuario = data.get("id_usuario")
    nuevo_salario = data.get("salario")
    fecha_salario = data.get("fecha_salario")

    if not id_usuario or not nuevo_salario:
        return jsonify({"error": "Faltan datos"}), 400

    DetallesUsuario.actualizar_salario(id_usuario, nuevo_salario, fecha_salario)

    return jsonify({"mensaje": "Salario actualizado correctamente"})


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
