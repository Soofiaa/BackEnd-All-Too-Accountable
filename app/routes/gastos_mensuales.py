import datetime
from flask import Blueprint, request, jsonify
from app.models.gasto_mensual import GastoMensual, db

gastos_mensuales_bp = Blueprint('gastos', __name__)

# Obtener todos los gastos del usuario
@gastos_mensuales_bp.route('', methods=['GET'])
def obtener_gastos():
    id_usuario = request.args.get('id_usuario')
    if not id_usuario:
        return jsonify({'error': 'Falta el id_usuario'}), 400

    gastos = GastoMensual.query.filter_by(id_usuario=id_usuario).all()
    return jsonify([gasto.to_dict() for gasto in gastos])

# Crear nuevo gasto
@gastos_mensuales_bp.route('', methods=['POST'])
def crear_gasto():
    data = request.json

    nombre = data.get('nombre', '').strip()
    monto = data.get('monto')
    dia_pago = data.get('dia_pago')
    id_usuario = data.get('id_usuario')

    if not nombre or not monto or not dia_pago or not id_usuario:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    nuevo_gasto = GastoMensual(
        nombre=nombre,
        descripcion=data.get('descripcion', ''),
        monto=monto,
        dia_pago=dia_pago,
        id_usuario=id_usuario
    )

    db.session.add(nuevo_gasto)
    db.session.commit()
    return jsonify(nuevo_gasto.to_dict()), 201

# Editar un gasto existente
@gastos_mensuales_bp.route('/<int:id_gasto>', methods=['PUT'])
def editar_gasto(id_gasto):
    data = request.json
    id_usuario = data.get('id_usuario')
    if not id_usuario:
        return jsonify({'error': 'id_usuario requerido'}), 400

    gasto = GastoMensual.query.filter_by(id_gasto=id_gasto, id_usuario=id_usuario).first()
    if not gasto:
        return jsonify({'error': 'Gasto no encontrado o no autorizado'}), 404

    # Extraer y validar campos obligatorios
    nombre = data.get('nombre', '').strip()
    monto = data.get('monto')
    dia_pago = data.get('dia_pago')

    if not nombre or not monto or not dia_pago:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    # Aplicar cambios
    gasto.nombre = nombre
    gasto.descripcion = data.get('descripcion', '')
    gasto.monto = float(monto)
    gasto.dia_pago = dia_pago

    db.session.commit()
    return jsonify(gasto.to_dict())

# Eliminar un gasto
@gastos_mensuales_bp.route('/<int:id_gasto>', methods=['DELETE'])
def eliminar_gasto(id_gasto):
    id_usuario = request.args.get('id_usuario')
    if not id_usuario:
        return jsonify({'error': 'id_usuario requerido'}), 400

    gasto = GastoMensual.query.filter_by(id_gasto=id_gasto, id_usuario=id_usuario).first()
    if not gasto:
        return jsonify({'error': 'Gasto no encontrado o no autorizado'}), 404

    db.session.delete(gasto)
    db.session.commit()
    return '', 204
