from flask import Blueprint, jsonify

transacciones_bp = Blueprint('transacciones', __name__)

@transacciones_bp.route('/')
def listar_transacciones():
    return jsonify({"mensaje": "Transacciones funcionando correctamente"})
