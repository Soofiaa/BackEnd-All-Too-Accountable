from flask import Blueprint, request, jsonify
from app import db
from app.models.transaccion import Transaccion
from app.models.promedio_categoria import PromedioCategoria
from datetime import date

promedios_bp = Blueprint("promedios", __name__)

@promedios_bp.route("/registrar_promedios/<int:id_usuario>", methods=["POST"])
def registrar_promedios_mensuales(id_usuario):
    hoy = date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year

    # Verifica que no exista ya un promedio registrado para este mes
    existente = PromedioCategoria.query.filter_by(id_usuario=id_usuario, mes=mes_actual, anio=anio_actual).first()
    if existente:
        return jsonify({"mensaje": "Ya existe un registro de promedios para este mes."}), 200

    # Obtiene todas las transacciones del mes actual
    transacciones = Transaccion.query.filter(
        Transaccion.id_usuario == id_usuario,
        Transaccion.tipo == "gasto",
        db.extract("month", Transaccion.fecha) == mes_actual,
        db.extract("year", Transaccion.fecha) == anio_actual,
        Transaccion.visible == True
    ).all()

    # Agrupa por categoría
    suma_por_categoria = {}
    for t in transacciones:
        if t.id_categoria not in suma_por_categoria:
            suma_por_categoria[t.id_categoria] = 0
        suma_por_categoria[t.id_categoria] += float(t.monto)

    # Inserta los promedios
    for id_categoria, total in suma_por_categoria.items():
        nuevo_promedio = PromedioCategoria(
            id_usuario=id_usuario,
            id_categoria=id_categoria,
            mes=mes_actual,
            anio=anio_actual,
            monto_total=total
        )
        db.session.add(nuevo_promedio)

    db.session.commit()
    return jsonify({"mensaje": "Promedios registrados correctamente."}), 201


@promedios_bp.route("/promedio_categoria", methods=["GET"])
def obtener_promedios_recientes():
    id_usuario = request.args.get("id_usuario")
    id_categoria = request.args.get("id_categoria")

    if not id_usuario or not id_categoria:
        return jsonify({"error": "Faltan parámetros"}), 400

    promedios = PromedioCategoria.query.filter_by(
        id_usuario=id_usuario,
        id_categoria=id_categoria
    ).order_by(PromedioCategoria.anio.desc(), PromedioCategoria.mes.desc()).limit(3).all()

    if not promedios:
        return jsonify({"promedio": 0})

    promedio_final = sum([p.monto_total for p in promedios]) / len(promedios)
    return jsonify({"promedio": round(promedio_final, 2)})
