from flask import Blueprint, request, jsonify
from app.models.gasto_mensual import GastoMensual, db
from app.models.transaccion import Transaccion
from database import conectar_bd
from flask import Blueprint, request, jsonify
from datetime import date

gastos_mensuales_bp = Blueprint('gastos_mensuales', __name__)

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

    # Validaciones
    if not nombre or len(nombre) > 100:
        return jsonify({'error': 'Nombre inválido'}), 400

    if not isinstance(monto, (int, float)) or float(monto) <= 0:
        return jsonify({'error': 'Monto inválido'}), 400

    if not isinstance(dia_pago, int) or not (1 <= dia_pago <= 28):
        return jsonify({'error': 'Día de pago inválido'}), 400

    if not id_usuario:
        return jsonify({'error': 'id_usuario es obligatorio'}), 400

    # Crear el gasto mensual
    nuevo_gasto = GastoMensual(
        nombre=nombre,
        descripcion=data.get('descripcion', ''),
        monto=monto,
        dia_pago=dia_pago,
        id_usuario=id_usuario,
        id_categoria=id_categoria
    )

    db.session.add(nuevo_gasto)
    db.session.commit()

    # Calcular fecha correcta del gasto
    hoy = date.today()
    anio = hoy.year
    mes = hoy.month
    dia = int(dia_pago)

    try:
        fecha_gasto = date(anio, mes, dia)
    except ValueError:
        # por si ponen 31 en un mes con 30 días
        fecha_gasto = date(anio, mes, 28)

    # Crear la transacción correspondiente
    id_categoria = data.get("id_categoria")

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

    if not nombre or len(nombre) > 100:
        return jsonify({'error': 'Nombre inválido'}), 400

    if not isinstance(monto, (int, float)) or float(monto) <= 0:
        return jsonify({'error': 'Monto inválido'}), 400

    if not isinstance(dia_pago, int) or not (1 <= dia_pago <= 28):
        return jsonify({'error': 'Día de pago inválido'}), 400

    # Aplicar cambios al gasto mensual
    gasto.nombre = nombre
    gasto.descripcion = data.get('descripcion', '')
    gasto.monto = float(monto)
    gasto.dia_pago = dia_pago
    gasto.id_categoria = data.get("id_categoria", gasto.id_categoria)

    db.session.commit()

    # Actualizar transacciones futuras asociadas a este gasto mensual
    hoy = date.today()

    transacciones = Transaccion.query.filter(
        Transaccion.id_gasto_mensual == gasto.id_gasto,
        Transaccion.fecha >= hoy
    ).all()

    for t in transacciones:
        t.descripcion = gasto.nombre
        t.monto = gasto.monto
        t.id_categoria = gasto.id_categoria

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


@gastos_mensuales_bp.route("/desactivar/<int:id_gasto>", methods=["PUT"])
def desactivar_gasto(id_gasto):
    id_usuario = request.args.get("id_usuario")
    if not id_usuario:
        return jsonify({"error": "id_usuario requerido"}), 400

    gasto = GastoMensual.query.filter_by(id_gasto=id_gasto, id_usuario=id_usuario).first()
    if not gasto:
        return jsonify({"error": "Gasto no encontrado o no autorizado"}), 404

    gasto.activo = False
    db.session.commit()
    return jsonify({"mensaje": "Gasto mensual desactivado"}), 200


@gastos_mensuales_bp.route("/reactivar/<int:id_gasto>", methods=["PUT"])
def reactivar_gasto(id_gasto):
    id_usuario = request.args.get("id_usuario")
    if not id_usuario:
        return jsonify({"error": "id_usuario requerido"}), 400

    gasto = GastoMensual.query.filter_by(id_gasto=id_gasto, id_usuario=id_usuario).first()
    if not gasto:
        return jsonify({"error": "Gasto no encontrado o no autorizado"}), 404

    gasto.activo = True
    db.session.commit()
    return jsonify({"mensaje": "Gasto mensual reactivado"}), 200