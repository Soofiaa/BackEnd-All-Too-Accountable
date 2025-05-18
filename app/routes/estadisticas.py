from flask import Blueprint, request, jsonify
from app.models.transaccion import Transaccion
from database import db

estadisticas_bp = Blueprint("estadisticas", __name__)

@estadisticas_bp.route("/comparar_categorias", methods=["GET"])
def comparar_categorias():
    id_usuario = request.args.get("id_usuario")
    mes1 = int(request.args.get("mes1"))
    anio1 = int(request.args.get("anio1"))
    mes2 = int(request.args.get("mes2"))
    anio2 = int(request.args.get("anio2"))

    if not id_usuario:
        return jsonify({"error": "Falta id_usuario"}), 400

    def obtener_totales(mes, anio):
        transacciones = Transaccion.query.filter(
            Transaccion.id_usuario == id_usuario,
            Transaccion.tipo == "gasto",
            db.extract("month", Transaccion.fecha) == mes,
            db.extract("year", Transaccion.fecha) == anio,
            Transaccion.visible == True
        ).all()

        resumen = {}
        for t in transacciones:
            cat = t.id_categoria
            resumen[cat] = resumen.get(cat, 0) + float(t.monto)
        return resumen

    totales1 = obtener_totales(mes1, anio1)
    totales2 = obtener_totales(mes2, anio2)

    categorias = set(list(totales1.keys()) + list(totales2.keys()))
    resultado = []

    for cat in categorias:
        valor1 = totales1.get(cat, 0)
        valor2 = totales2.get(cat, 0)
        cambio = valor2 - valor1
        porcentaje = ((valor2 - valor1) / valor1 * 100) if valor1 > 0 else None

        resultado.append({
            "id_categoria": cat,
            "monto_mes1": valor1,
            "monto_mes2": valor2,
            "cambio": cambio,
            "porcentaje": porcentaje
        })

    return jsonify(resultado)
