from flask import Blueprint, request, jsonify
from app.models.ahorro import MovimientoAhorro
from database import db
from datetime import datetime

mov_ahorro_bp = Blueprint("movimientos_ahorro", __name__)

@mov_ahorro_bp.route('', methods=['POST'])
def registrar_movimiento():
    data = request.json
    id_usuario = data.get('id_usuario')
    tipo = data.get('tipo')  # 'agregar' o 'quitar'
    monto = data.get('monto')
    fecha = data.get('fecha', datetime.now().date())

    if not all([id_usuario, tipo, monto]):
        return jsonify({'error': 'Faltan datos'}), 400

    nuevo = MovimientoAhorro(
        id_usuario=id_usuario,
        tipo=tipo,
        monto=monto,
        fecha=fecha
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201

@mov_ahorro_bp.route('', methods=['GET'])
def obtener_movimientos():
    id_usuario = request.args.get('id_usuario')
    if not id_usuario:
        return jsonify({'error': 'id_usuario requerido'}), 400

    movimientos = MovimientoAhorro.query.filter_by(id_usuario=id_usuario).order_by(MovimientoAhorro.fecha).all()
    return jsonify([m.to_dict() for m in movimientos])
