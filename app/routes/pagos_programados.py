from flask import Blueprint, jsonify, request
from app.models.transaccion import Transaccion
from app.models.pago_programado import GastoProgramado
from app import db
from datetime import date, datetime, timedelta
from database import conectar_bd

gastos_programados_bp = Blueprint("gastos_programados", __name__)


# POST - Crear gasto programado
@gastos_programados_bp.route("", methods=["POST", "OPTIONS"])
def crear_gasto_programado():
    if request.method == "OPTIONS":
        return jsonify({"status": "CORS preflight"}), 200

    data = request.json

    try:
        fecha_emision = datetime.strptime(data["fecha_emision"], "%Y-%m-%d").date()
        tipo_pago = data["tipo_pago"]
        id_categoria = data.get("id_categoria")

        if tipo_pago == "cheque":
            dias_cheque = int(data["dias_cheque"])
            fecha_transaccion = fecha_emision + timedelta(days=dias_cheque)
        else:
            dias_cheque = None
            fecha_transaccion = fecha_emision

        nuevo = GastoProgramado(
            id_usuario=data["id_usuario"],
            tipo_pago=tipo_pago,
            descripcion=data["descripcion"],
            fecha_emision=fecha_emision,
            dias_cheque=dias_cheque,
            monto=data["monto"],
            fecha_transaccion=fecha_transaccion,
            id_categoria=id_categoria
        )

        db.session.add(nuevo)
        db.session.commit()
        return jsonify(nuevo.to_dict()), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# GET - Obtener todos los gastos programados de un usuario
@gastos_programados_bp.route("/<int:id_usuario>", methods=["GET"])
def obtener_gastos_programados(id_usuario):
    gastos = GastoProgramado.query.filter_by(id_usuario=id_usuario).all()
    return jsonify([g.to_dict() for g in gastos]), 200


# PUT - Editar gasto programado
@gastos_programados_bp.route("/<int:id_gasto_programado>", methods=["PUT"])
def editar_gasto_programado(id_gasto_programado):
    from datetime import date

    data = request.json
    gasto = GastoProgramado.query.get(id_gasto_programado)

    if not gasto:
        return jsonify({"error": "Gasto no encontrado"}), 404

    try:
        gasto.tipo_pago = data["tipo_pago"]
        gasto.descripcion = data["descripcion"]
        gasto.fecha_emision = datetime.strptime(data["fecha_emision"], "%Y-%m-%d").date()
        gasto.dias_cheque = int(data["dias_cheque"]) if data["tipo_pago"] == "cheque" else None
        gasto.monto = data["monto"]
        gasto.fecha_transaccion = gasto.fecha_emision + timedelta(days=gasto.dias_cheque) if gasto.dias_cheque else gasto.fecha_emision
        gasto.id_categoria = data.get("id_categoria", gasto.id_categoria)

        db.session.commit()

        # Actualizar transacciones futuras vinculadas a este gasto programado
        hoy = date.today()

        transacciones = Transaccion.query.filter_by(
            id_gasto_programado = gasto.id_gasto_programado
        ).all()

        for t in transacciones:
            t.descripcion = gasto.descripcion
            t.monto = gasto.monto
            t.id_categoria = gasto.id_categoria

        db.session.commit()

        return jsonify(gasto.to_dict()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# DELETE - Eliminar gasto programado
@gastos_programados_bp.route("/<int:id_gasto_programado>", methods=["DELETE"])
def eliminar_gasto_programado(id_gasto_programado):
    gasto = GastoProgramado.query.get(id_gasto_programado)

    if not gasto:
        return jsonify({"error": "Gasto no encontrado"}), 404

    db.session.delete(gasto)
    db.session.commit()
    return jsonify({"mensaje": "Gasto eliminado correctamente"}), 200


@gastos_programados_bp.route("/actualizar_estado_automatico/<int:id_usuario>", methods=["PUT"])
def actualizar_estado_programados(id_usuario):
    hoy = date.today()

    gastos = GastoProgramado.query.filter_by(id_usuario=id_usuario, activo=True).all()
    actualizados = 0

    for g in gastos:
        if g.fecha_transaccion < hoy:
            g.activo = False
            actualizados += 1

    db.session.commit()
    return jsonify({"mensaje": f"{actualizados} pagos programados marcados como inactivos."}), 200
