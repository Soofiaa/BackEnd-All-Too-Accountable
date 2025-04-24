from flask import Blueprint, jsonify, request
from app.models.pago_pendiente import PagoPendiente

pagos_pendientes_bp = Blueprint('pagos_pendientes', __name__)

@pagos_pendientes_bp.route('', methods=['GET'])
def obtener_pagos_pendientes():
    try:
        id_usuario = request.args.get("id_usuario")
        if not id_usuario:
            return jsonify({"error": "Falta el parámetro id_usuario"}), 400

        pagos = PagoPendiente.obtener_por_usuario(id_usuario)
        return jsonify(pagos), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@pagos_pendientes_bp.route('/<int:id_pago>', methods=['PUT'])
def actualizar_pago(id_pago):
    data = request.get_json()
    nuevas_cuotas = data.get('cuotasPagadas')

    if nuevas_cuotas is None:
        return jsonify({'error': 'Falta el campo cuotasPagadas'}), 400

    try:
        PagoPendiente.actualizar_cuotas(id_pago, nuevas_cuotas)
        return jsonify({'mensaje': 'Pago actualizado correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
