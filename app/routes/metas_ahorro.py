from flask import Blueprint, request, jsonify
from database import db
from app.models.meta_ahorro import MetaAhorro
from datetime import datetime

metas_ahorro_bp = Blueprint('metas_ahorro_bp', __name__)

# Obtener metas por usuario
@metas_ahorro_bp.route('/<int:id_usuario>', methods=['GET'])
def obtener_metas(id_usuario):
    metas = MetaAhorro.query.filter_by(id_usuario=id_usuario).all()
    return jsonify([meta.serialize() for meta in metas]), 200

# Crear una nueva meta
@metas_ahorro_bp.route('', methods=['POST'])
def crear_meta():
    data = request.json
    print("JSON recibido en backend:", data)

    titulo = data.get("titulo", "").strip()
    fecha_limite = data.get("fecha_limite")
    monto_meta = data.get("monto_meta")
    id_usuario = data.get("id_usuario")

    if not titulo or not fecha_limite or not monto_meta or not id_usuario:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    nueva_meta = MetaAhorro(
        titulo=titulo,
        fecha_limite=datetime.strptime(fecha_limite, '%Y-%m-%d'),
        monto_meta=monto_meta,
        id_usuario=id_usuario
    )
    db.session.add(nueva_meta)
    db.session.commit()
    db.session.refresh(nueva_meta)  # asegura que los datos estén frescos

    return jsonify(nueva_meta.serialize()), 201

# Editar una meta existente
@metas_ahorro_bp.route('/<int:id_meta>', methods=['PUT'])
def editar_meta(id_meta):
    meta = MetaAhorro.query.get_or_404(id_meta)
    data = request.json

    titulo = data.get("titulo", "").strip()
    fecha_limite = data.get("fecha_limite")
    monto_meta = data.get("monto_meta")

    if not titulo or not fecha_limite or not monto_meta:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    meta.titulo = titulo
    meta.fecha_limite = datetime.fromisoformat(fecha_limite).date()
    meta.monto_meta = monto_meta

    db.session.commit()
    return jsonify(meta.serialize()), 200

# Eliminar una meta
@metas_ahorro_bp.route('/<int:id_meta>', methods=['DELETE'])
def eliminar_meta(id_meta):
    meta = MetaAhorro.query.get_or_404(id_meta)
    db.session.delete(meta)
    db.session.commit()
    return jsonify({"mensaje": "Meta eliminada correctamente"}), 200