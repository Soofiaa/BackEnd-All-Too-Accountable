from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from app import db
from app.models.categoria import Categoria
from app.models.transaccion import Transaccion
from app.models.gasto_mensual import GastoMensual
from app.models.pago_programado import GastoProgramado
from sqlalchemy import case

categorias_bp = Blueprint("categorias", __name__)

# Obtener todas las categorías del usuario + "General"
@categorias_bp.route("/<int:id_usuario>", methods=["GET"])
def obtener_categorias(id_usuario):
    orden = case(
        (Categoria.nombre == "General", 1),
        (Categoria.nombre == "Gasto Mensual", 2),
        (Categoria.nombre == "Gasto Programado", 3),
        else_=4
    )

    categorias = Categoria.query.filter(
        (Categoria.id_usuario == id_usuario) | (Categoria.id_usuario == None)
    ).order_by(orden, Categoria.nombre).all()

    return jsonify([c.to_dict() for c in categorias])


# Crear nueva categoría
@categorias_bp.route("/", methods=["POST"])
def crear_categoria():
    data = request.get_json()
    nombre = data.get("nombre", "").strip()
    tipo = data.get("tipo", "").strip()
    id_usuario = data.get("id_usuario")
    monto_limite = data.get("monto_limite", 0)

    # Validación de campos obligatorios
    if not nombre or not tipo or not id_usuario:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    # Validar longitud de nombre
    if len(nombre) < 2 or len(nombre) > 50:
        return jsonify({"error": "El nombre debe tener entre 2 y 50 caracteres"}), 400

    # Validar tipo permitido
    if tipo not in ["ingreso", "gasto", "ambos"]:
        return jsonify({"error": "Tipo de categoría inválido"}), 400

    # Si es tipo ingreso, se fuerza monto_limite a 0
    if tipo.lower() == "ingreso":
        monto_limite = 0
    else:
        try:
            monto_limite = float(monto_limite)
            if monto_limite < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"error": "Monto límite inválido"}), 400

    # Validar duplicado
    existente = Categoria.query.filter_by(nombre=nombre, id_usuario=id_usuario).first()
    if existente:
        return jsonify({"error": "Ya existe una categoría con ese nombre"}), 400

    nueva = Categoria(nombre=nombre, tipo=tipo, id_usuario=id_usuario, monto_limite=monto_limite)
    db.session.add(nueva)
    db.session.commit()

    return jsonify(nueva.to_dict()), 201


# Editar categoría
@categorias_bp.route("/<int:id>", methods=["PUT"])
def editar_categoria(id):
    categoria = Categoria.query.get(id)
    if not categoria:
        return jsonify({"error": "Categoría no encontrada"}), 404

    # Protegemos categoría "General" o global
    if categoria.id_usuario is None and categoria.nombre == "General":
        return jsonify({"error": "Esta categoría no se puede editar"}), 403

    data = request.get_json()

    nombre = data.get("nombre", categoria.nombre).strip()
    tipo = data.get("tipo", categoria.tipo).strip()
    monto_limite = data.get("monto_limite", categoria.monto_limite)

    # Validar nombre
    if len(nombre) < 2 or len(nombre) > 50:
        return jsonify({"error": "El nombre debe tener entre 2 y 50 caracteres"}), 400

    # Validar tipo permitido
    if tipo not in ["ingreso", "gasto", "ambos"]:
        return jsonify({"error": "Tipo de categoría inválido"}), 400

    # Si es ingreso, el monto límite debe ser 0
    if tipo.lower() == "ingreso":
        monto_limite = 0
    else:
        try:
            monto_limite = float(monto_limite)
            if monto_limite < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"error": "Monto límite inválido"}), 400

    # Asignar cambios
    categoria.nombre = nombre
    categoria.tipo = tipo
    categoria.monto_limite = monto_limite

    db.session.commit()

    return jsonify({"mensaje": "Categoría actualizada"}), 200


# Eliminar categoría
@categorias_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_categoria(id):
    categoria = Categoria.query.get(id)
    if not categoria:
        return jsonify({"error": "Categoría no encontrada"}), 404

    # Protegemos la categoría "General"
    if categoria.es_general:
        return jsonify({"error": "Esta categoría no se puede eliminar"}), 403

    id_usuario = categoria.id_usuario

    # Buscar la categoría general del sistema (común o del mismo usuario si aplica)
    categoria_general = Categoria.query.filter_by(nombre="General", id_usuario=None).first()
    if not categoria_general:
        return jsonify({"error": "No se encontró la categoría general"}), 500

    id_general = categoria_general.id_categoria

    # Reasignar en transacciones
    Transaccion.query.filter_by(id_categoria=id).update({Transaccion.id_categoria: id_general})
    # Reasignar en gastos mensuales
    GastoMensual.query.filter_by(id_categoria=id).update({GastoMensual.id_categoria: id_general})
    # Reasignar en pagos programados
    GastoProgramado.query.filter_by(id_categoria=id).update({GastoProgramado.id_categoria: id_general})

    # Eliminar la categoría
    db.session.delete(categoria)
    db.session.commit()

    return jsonify({"mensaje": "Categoría eliminada y transacciones reasignadas a 'General'"}), 200
