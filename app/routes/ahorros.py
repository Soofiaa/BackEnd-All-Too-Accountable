from flask import Blueprint, request, jsonify
from app.models.ahorro import MovimientoAhorro
from database import db
from datetime import datetime

mov_ahorro_bp = Blueprint("movimientos_ahorro", __name__)

@mov_ahorro_bp.route('', methods=['POST'])
def registrar_movimiento():
    data = request.json
    id_usuario = data.get('id_usuario')
    tipo = data.get('tipo')
    monto = data.get('monto')
    fecha = data.get('fecha', datetime.now().date())

    # Validaciones
    if not id_usuario:
        return jsonify({'error': 'id_usuario es obligatorio'}), 400

    if tipo not in ['agregar', 'quitar']:
        return jsonify({'error': "Tipo inválido. Debe ser 'agregar' o 'quitar'"}), 400

    try:
        monto = float(monto)
        if monto <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'error': 'Monto inválido'}), 400

    try:
        # permite str tipo "2024-05-21" o datetime.date
        fecha = datetime.strptime(str(fecha), "%Y-%m-%d").date()
    except Exception:
        fecha = datetime.now().date()  # fallback si viene vacío o mal

    # Crear y guardar
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
    try:
        id_usuario = int(id_usuario)
    except (ValueError, TypeError):
        return jsonify({'error': 'id_usuario inválido'}), 400

    movimientos = MovimientoAhorro.query.filter_by(id_usuario=id_usuario).order_by(MovimientoAhorro.fecha).all()
    return jsonify([m.to_dict() for m in movimientos])
