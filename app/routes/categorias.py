from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from app import db
from app.models.categoria import Categoria

categorias_bp = Blueprint("categorias", __name__)

# Obtener todas las categorías del usuario + "General"
@categorias_bp.route("/<int:id_usuario>", methods=["GET"])
def obtener_categorias(id_usuario):
    # Filtramos categorías propias y globales (id_usuario == None → "General")
    categorias = Categoria.query.filter(
        or_(Categoria.id_usuario == id_usuario, Categoria.id_usuario == None)
    ).all()

    # Retornamos los datos + si se pueden editar
    resultado = [
        {
            "id": c.id_categoria,
            "nombre": c.nombre,
            "tipo": c.tipo,
            "editable": c.id_usuario is not None  # Solo si no es "General"
        } for c in categorias
    ]
    return jsonify(resultado), 200

# Crear nueva categoría
@categorias_bp.route("/", methods=["POST"])
def crear_categoria():
    data = request.get_json()
    nombre = data.get("nombre")
    tipo = data.get("tipo")
    id_usuario = data.get("id_usuario")

    # Validación básica
    if not nombre or not tipo or not id_usuario:
        return jsonify({"error": "Faltan datos"}), 400

    # Validamos que no exista otra categoría igual para ese usuario
    existente = Categoria.query.filter_by(nombre=nombre, id_usuario=id_usuario).first()
    if existente:
        return jsonify({"error": "Ya existe una categoría con ese nombre"}), 400

    nueva = Categoria(nombre=nombre, tipo=tipo, id_usuario=id_usuario)
    db.session.add(nueva)
    db.session.commit()

    return jsonify({"mensaje": "Categoría creada con éxito"}), 201

# Editar categoría
@categorias_bp.route("/<int:id>", methods=["PUT"])
def editar_categoria(id):
    categoria = Categoria.query.get(id)
    if not categoria:
        return jsonify({"error": "Categoría no encontrada"}), 404

    # Protegemos la categoría "General"
    if categoria.id_usuario is None and categoria.nombre == "General":
        return jsonify({"error": "Esta categoría no se puede editar"}), 403

    data = request.get_json()
    categoria.nombre = data.get("nombre", categoria.nombre)
    categoria.tipo = data.get("tipo", categoria.tipo)
    db.session.commit()

    return jsonify({"mensaje": "Categoría actualizada"}), 200

# Eliminar categoría
@categorias_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_categoria(id):
    categoria = Categoria.query.get(id)
    if not categoria:
        return jsonify({"error": "Categoría no encontrada"}), 404

    # Protegemos la categoría "General"
    if categoria.id_usuario is None and categoria.nombre == "General":
        return jsonify({"error": "Esta categoría no se puede eliminar"}), 403

    db.session.delete(categoria)
    db.session.commit()
    return jsonify({"mensaje": "Categoría eliminada"}), 200
