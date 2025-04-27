# routes/detalles_usuario.py

from flask import Blueprint, request, jsonify
from database import conectar_bd

detalles_usuario_bp = Blueprint('detalles_usuario', __name__)

from app.models.detalle_usuario import DetallesUsuario

@detalles_usuario_bp.route("/api/detalles_usuario", methods=["GET"])
def obtener_detalles_usuario():
    id_usuario = request.args.get("id_usuario")
    print("📥 Recibida petición para id_usuario:", id_usuario)

    db = conectar_bd()
    cursor = db.cursor()

    # ✅ Consulta a la BD
    cursor.execute("SELECT salario, ahorros, dia_facturacion FROM detalles_usuario WHERE id_usuario = %s", (id_usuario,))
    resultado = cursor.fetchone()

    print("🧪 RAW resultado desde BD:", resultado)

    if not resultado:
        nuevo = DetallesUsuario(id_usuario, 0, 0, 1)
        nuevo.guardar()
        resultado = (0, 0, 1)

    detalles_dict = resultado

    # ✅ Consulta de nombre
    cursor.execute("SELECT nombre_usuario FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    usuario = cursor.fetchone()
    usuario_dict = usuario if usuario else {}

    print("🧪 DEBUG → Detalles:", detalles_dict)
    print("🧪 DEBUG → Usuario:", usuario_dict)

    return jsonify({**detalles_dict, **usuario_dict})


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
