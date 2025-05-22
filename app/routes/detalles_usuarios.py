from datetime import datetime
from flask import Blueprint, request, jsonify
from database import conectar_bd
from app.models.detalle_usuario import DetallesUsuario
from app.routes.transacciones_completas import actualizar_salarios_existentes

detalles_usuario_bp = Blueprint('detalles_usuario', __name__)
        
@detalles_usuario_bp.route('/api/detalles_usuario', methods=['GET'])
def obtener_detalles_usuario():
    id_usuario = request.args.get('id_usuario')
    detalles = DetallesUsuario.obtener_por_id(id_usuario)
    if detalles:
        return jsonify(detalles)
    else:
        return jsonify({"error": "Detalles no encontrados"}), 404


@detalles_usuario_bp.route("/api/actualizar_salario", methods=["POST"])
def actualizar_salario():
    data = request.json
    id_usuario = data.get("id_usuario")
    nuevo_salario = data.get("salario")
    fecha_salario = data.get("fecha_salario")

    if not id_usuario:
        return jsonify({"error": "id_usuario es obligatorio"}), 400

    try:
        nuevo_salario = float(nuevo_salario)
        if nuevo_salario <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Salario inválido"}), 400

    if fecha_salario:
        try:
            # Validar formato y guardar como string limpio
            fecha_salario = datetime.strptime(fecha_salario, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD"}), 400
    else:
        # Si no se especifica, usar fecha actual (en formato YYYY-MM-DD)
        fecha_salario = datetime.today().strftime("%Y-%m-%d")

    DetallesUsuario.actualizar_salario(id_usuario, nuevo_salario, fecha_salario)
    actualizar_salarios_existentes(int(id_usuario))

    return jsonify({"mensaje": "Salario actualizado correctamente"})


@detalles_usuario_bp.route("/api/actualizar_nombre", methods=["POST"])
def actualizar_nombre_usuario():
    data = request.json
    id_usuario = data.get("id_usuario")
    nuevo_nombre = data.get("nombre_usuario", "").strip()

    if not id_usuario:
        return jsonify({"error": "id_usuario es obligatorio"}), 400

    if not nuevo_nombre or len(nuevo_nombre) < 2 or len(nuevo_nombre) > 100:
        return jsonify({"error": "Nombre inválido. Debe tener entre 2 y 100 caracteres"}), 400

    db = conectar_bd()
    cursor = db.cursor()
    cursor.execute("UPDATE usuarios SET nombre_usuario = %s WHERE id_usuario = %s", (nuevo_nombre, id_usuario))
    db.commit()

    return jsonify({"mensaje": "Nombre actualizado correctamente"})


@detalles_usuario_bp.route('/api/historial_salarios/<int:id_usuario>', methods=['GET'])
def historial_salarios(id_usuario):
    try:
        historial = DetallesUsuario.obtener_historial(id_usuario)
        return jsonify(historial), 200
    except Exception as e:
        print(f"Error al obtener historial de salarios: {e}")
        return jsonify({"error": "Error al obtener historial de salarios"}), 500


@detalles_usuario_bp.route('/editar_salario/<int:id_detalle>', methods=['PUT'])
def editar_salario(id_detalle):
    try:
        datos = request.get_json()
        nuevo_salario = datos.get("salario")
        nueva_fecha = datos.get("fecha_salario")

        if not nuevo_salario or not nueva_fecha:
            return jsonify({"error": "Faltan datos"}), 400

        # Validar formato fecha
        try:
            nueva_fecha = datetime.strptime(nueva_fecha, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido"}), 400

        db = conectar_bd()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE detalles_usuario
            SET salario = %s, fecha_salario = %s
            WHERE id_detalle = %s
        """, (nuevo_salario, nueva_fecha, id_detalle))
        db.commit()
        return jsonify({"mensaje": "Salario editado correctamente"}), 200

    except Exception as e:
        print("Error al editar salario:", e)
        return jsonify({"error": "No se pudo editar"}), 500

    finally:
        db.close()
        