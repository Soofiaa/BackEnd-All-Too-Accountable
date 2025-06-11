from flask import Blueprint, request, jsonify
from database import db
from app.models.meta_ahorro import MetaAhorro
from datetime import datetime, date

metas_ahorro_bp = Blueprint('metas_ahorro_bp', __name__)


# Obtener metas por usuario
@metas_ahorro_bp.route('/<int:id_usuario>', methods=['GET'])
def obtener_metas(id_usuario):
    hoy = date.today()

    # Desactivar metas vencidas
    metas_vencidas = MetaAhorro.query.filter_by(id_usuario=id_usuario, activa=True)\
        .filter(MetaAhorro.fecha_limite < hoy).all()
    for meta in metas_vencidas:
        meta.activa = False

    # Activar la próxima meta futura si no hay ninguna activa
    hay_activa = MetaAhorro.query.filter_by(id_usuario=id_usuario, activa=True).first()
    if not hay_activa:
        proxima_meta = MetaAhorro.query.filter_by(id_usuario=id_usuario)\
            .filter(MetaAhorro.fecha_limite >= hoy)\
            .order_by(MetaAhorro.fecha_limite.asc()).first()
        if proxima_meta:
            proxima_meta.activa = True

    db.session.commit()

    # Devolver todas las metas
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

    # Validación adicional
    try:
        monto_meta = float(monto_meta)
        if monto_meta <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Monto inválido"}), 400

    nueva_meta = MetaAhorro(
        titulo=titulo,
        fecha_limite=datetime.strptime(fecha_limite, '%d-%m-%Y').date(),
        monto_meta=monto_meta,
        id_usuario=id_usuario
    )
    db.session.add(nueva_meta)
    db.session.commit()
    db.session.refresh(nueva_meta)

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
    
    try:
        meta.fecha_limite = datetime.strptime(fecha_limite, '%d-%m-%Y').date()
    except ValueError:
        return jsonify({"error": "Fecha inválida. Usa formato DD-MM-YYYY"}), 400

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