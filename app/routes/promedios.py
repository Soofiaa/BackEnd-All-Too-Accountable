from flask import Blueprint, request, jsonify
from app import db
from app.models.transaccion import Transaccion
from app.models.promedio_categoria import PromedioCategoria
from datetime import date

promedios_bp = Blueprint("promedios", __name__)

@promedios_bp.route("/registrar_promedios/<int:id_usuario>", methods=["POST"])
def registrar_promedios_mensuales(id_usuario):
    # Validar que el ID sea válido
    if not isinstance(id_usuario, int) or id_usuario <= 0:
        return jsonify({"error": "id_usuario inválido"}), 400

    hoy = date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year

    # Verifica si ya hay un registro de promedios para este mes
    existente = PromedioCategoria.query.filter_by(
        id_usuario=id_usuario,
        mes=mes_actual,
        anio=anio_actual
    ).first()

    if existente:
        return jsonify({"mensaje": "Ya existe un registro de promedios para este mes."}), 200

    # Obtiene todas las transacciones visibles tipo gasto del mes actual
    transacciones = Transaccion.query.filter(
        Transaccion.id_usuario == id_usuario,
        Transaccion.tipo == "gasto",
        db.extract("month", Transaccion.fecha) == mes_actual,
        db.extract("year", Transaccion.fecha) == anio_actual,
        Transaccion.visible == True
    ).all()

    # Agrupa montos por categoría
    suma_por_categoria = {}
    for t in transacciones:
        if t.id_categoria not in suma_por_categoria:
            suma_por_categoria[t.id_categoria] = 0
        suma_por_categoria[t.id_categoria] += float(t.monto)

    # Inserta los promedios por categoría
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
    try:
        id_usuario = int(request.args.get("id_usuario"))
        id_categoria = int(request.args.get("id_categoria"))
        if id_usuario <= 0 or id_categoria <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Parámetros inválidos"}), 400

    promedios = PromedioCategoria.query.filter_by(
        id_usuario=id_usuario,
        id_categoria=id_categoria
    ).order_by(PromedioCategoria.anio.desc(), PromedioCategoria.mes.desc()).limit(3).all()

    if not promedios:
        return jsonify({"promedio": 0})

    promedio_final = sum([p.monto_total for p in promedios]) / len(promedios)
    return jsonify({"promedio": round(promedio_final, 2)})
