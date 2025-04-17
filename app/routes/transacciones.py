from flask import Blueprint, request, jsonify
from database import db
from app.models.categoria import Categoria
from app.models.transaccion import Transaccion
from datetime import datetime
import base64

transacciones_bp = Blueprint("transacciones", __name__)

@transacciones_bp.route('/<int:id_usuario>', methods=['GET'])
def obtener_transacciones(id_usuario):
    transacciones = db.session.execute(
        db.select(Transaccion).filter_by(id_usuario=id_usuario, visible=True)
    ).scalars().all()

    resultado = [
        {
            "id": t.id_transaccion,
            "fecha": t.fecha,
            "monto": float(t.monto),
            "categoria": t.categoria,
            "descripcion": t.descripcion,
            "tipoPago": t.tipo_pago,
            "cuotas": t.cuotas,
            "interes": float(t.interes),
            "valorCuota": float(t.valor_cuota or 0),
            "totalCredito": float(t.total_credito or 0),
            "tipo": t.tipo,
            "repetido": t.se_repite,
        }
        for t in transacciones
    ]

    return jsonify(resultado)

@transacciones_bp.route("/", methods=["POST"])
def crear_transaccion():
    data = request.json

    try:
        nueva = Transaccion(
            fecha=datetime.strptime(data["fecha"], "%Y-%m-%d").date(),
            monto=data["monto"],
            categoria=data["categoria"],
            descripcion=data["descripcion"],
            tipo_pago=data["tipoPago"],
            imagen=base64.b64decode(data["imagen"]) if data.get("imagen") else None,
            cuotas=data.get("cuotas", 1),
            interes=data.get("interes", 0),
            valor_cuota=data.get("valorCuota"),
            total_credito=data.get("totalCredito"),
            tipo=data["tipo"],
            se_repite=data.get("repetido", False),
            id_usuario=data["id_usuario"],
            visible=True
        )

        db.session.add(nueva)
        db.session.commit()

        return jsonify({"mensaje": "Transacción guardada correctamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
