from flask import Blueprint, request, jsonify
from app.database import db
from app.models.transaccion import Transaccion
from datetime import datetime

transacciones_bp = Blueprint('transacciones', __name__)

# Crea una nueva transacción
@transacciones_bp.route('/transacciones', methods=['POST'])
def crear_transaccion():
    data = request.json
    try:
        transaccion = Transaccion(
            descripcion=data['descripcion'],
            monto=float(data['monto']),
            fecha=datetime.strptime(data['fecha'], '%Y-%m-%d'),
            categoria=data['categoria'],
            tipo=data['tipo']
        )
        db.session.add(transaccion)
        db.session.commit()
        return jsonify({"mensaje": "Transacción creada correctamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Muestra todas las transacciones visibles
@transacciones_bp.route('/transacciones', methods=['GET'])
def obtener_transacciones():
    transacciones = Transaccion.query.filter_by(visible=True).all()
    resultado = [{
        "id": t.id,
        "descripcion": t.descripcion,
        "monto": t.monto,
        "fecha": t.fecha.strftime('%Y-%m-%d'),
        "categoria": t.categoria,
        "tipo": t.tipo
    } for t in transacciones]
    return jsonify(resultado)

# Oculta la transacción en lugar de eliminarla
@transacciones_bp.route('/transacciones/<int:id>', methods=['DELETE'])
def eliminar_transaccion(id):
    transaccion = Transaccion.query.get(id)
    if not transaccion:
        return jsonify({"error": "Transacción no encontrada"}), 404
    
    transaccion.visible = False
    db.session.commit()
    return jsonify({"mensaje": "Transacción eliminada (oculta) correctamente"})

# Muestra todas las transacciones ocultas
@transacciones_bp.route('/transacciones/ocultas', methods=['GET'])
def obtener_transacciones_ocultas():
    transacciones = Transaccion.query.filter_by(visible=False).all()
    resultado = [{
        "id": t.id,
        "descripcion": t.descripcion,
        "monto": t.monto,
        "fecha": t.fecha.strftime('%Y-%m-%d'),
        "categoria": t.categoria,
        "tipo": t.tipo
    } for t in transacciones]
    return jsonify(resultado)

# Recupera una transacción oculta
@transacciones_bp.route('/transacciones/recuperar/<int:id>', methods=['PUT'])
def recuperar_transaccion(id):
    transaccion = Transaccion.query.get(id)
    if not transaccion:
        return jsonify({"error": "Transacción no encontrada"}), 404

    transaccion.visible = True
    db.session.commit()
    return jsonify({"mensaje": "Transacción recuperada con éxito"})
