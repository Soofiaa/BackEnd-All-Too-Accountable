from flask import Blueprint, request, jsonify
from app.models import db, Transaccion
from datetime import datetime

transacciones_bp = Blueprint("transacciones", __name__)

@transacciones_bp.route("/", methods=["POST"])
def crear_transaccion():
    data = request.get_json()

    try:
        nueva = Transaccion(
            fecha=datetime.strptime(data["fecha"], "%Y-%m-%d"),
            monto=float(data["monto"].replace(".", "")),
            categoria=data["categoria"],
            descripcion=data["descripcion"],
            tipo_pago=data["tipoPago"],
            imagen=None,  # Puedes manejar imagen en otro endpoint con `request.files`
            cuotas=int(data.get("cuotas", 1)),
            interes=float(data.get("interes", 0)),
            valor_cuota=float(data.get("valorCuota", 0)),
            total_credito=float(data.get("totalCredito", 0)),
            tipo=data["tipo"],
            se_repite=bool(data.get("repetido", False)),
            id_usuario=1,  # Por ahora fija, después usarás el ID del usuario logueado
            visible=True
        )
        db.session.add(nueva)
        db.session.commit()
        return jsonify({"mensaje": "Transacción guardada con éxito"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
