import os
from flask import Blueprint, request, jsonify
from database import db
from app.models.categoria import Categoria
from app.models.transaccion import Transaccion
from datetime import datetime
import base64
from app.models.pago_pendiente import PagoPendiente


transacciones_bp = Blueprint("transacciones", __name__)

@transacciones_bp.route('/<int:id_usuario>', methods=['GET'])
def obtener_transacciones(id_usuario):
    transacciones = db.session.execute(
        db.select(Transaccion).filter_by(id_usuario=id_usuario)
    ).scalars().all()

    resultado = [
        {
            "id": t.id_transaccion,
            "fecha": t.fecha,
            "monto": float(t.monto),
            "categoria": t.categoria,
            "descripcion": t.descripcion,
            "tipoPago": t.tipo_pago,
            "cuotas": t.cuotas,
            "interes": float(t.interes),
            "valorCuota": float(t.valor_cuota or 0),
            "totalCredito": float(t.total_credito or 0),
            "tipo": t.tipo,
            "repetido": t.se_repite,
            "imagen": f"/imagenes/{t.imagen}" if t.imagen else None,
            "visible": t.visible  # 👈 AÑADE ESTA LÍNEA
        }
        for t in transacciones
    ]


    return jsonify(resultado)

@transacciones_bp.route('/categorias/<int:id_usuario>', methods=['GET'])
def obtener_categorias(id_usuario):
    try:
        categorias = db.session.execute(
            db.select(Categoria).where(
                (Categoria.id_usuario == id_usuario) | (Categoria.es_general == True)
            )
        ).scalars().all()

        resultado = [
            { "nombre": c.nombre }
            for c in categorias
        ]

        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transacciones_bp.route("/", methods=["POST"])
def crear_transaccion():

    data = request.json
    CARPETA_IMAGENES = os.path.join(os.getcwd(), 'imagenes_transacciones')
    os.makedirs(CARPETA_IMAGENES, exist_ok=True)

    try:
        # Procesar imagen si viene
        imagen_filename = None
        if data.get("imagen"):
            imagen_bytes = base64.b64decode(data["imagen"])
            imagen_filename = f"transaccion_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            ruta_imagen = os.path.join(CARPETA_IMAGENES, imagen_filename)
            with open(ruta_imagen, 'wb') as f:
                f.write(imagen_bytes)

        nueva = Transaccion(
            fecha=datetime.strptime(data["fecha"], "%Y-%m-%d").date(),
            monto=data["monto"],
            categoria=data["categoria"],
            descripcion=data["descripcion"],
            tipo_pago=data["tipoPago"],
            imagen=imagen_filename,
            cuotas=data.get("cuotas", 1),
            interes=data.get("interes", 0),
            valor_cuota=data.get("valorCuota"),
            total_credito=data.get("totalCredito"),
            tipo=data["tipo"],
            se_repite=data.get("repetido", False),
            id_usuario=data["id_usuario"],
            visible=True
        )

        db.session.add(nueva)
        db.session.commit()

        # Crear pago pendiente si es con tarjeta de crédito en cuotas
        if nueva.tipo_pago == "credito" and nueva.cuotas > 1:
            pago = PagoPendiente(
                id_usuario=nueva.id_usuario,
                id_transaccion=nueva.id_transaccion,
                descripcion=nueva.descripcion,
                fecha=nueva.fecha,
                cuotas=nueva.cuotas,
                valorCuota=nueva.valor_cuota
            )
            pago.guardar()

        return jsonify({
            "id_transaccion": nueva.id_transaccion,
            "fecha": nueva.fecha.strftime("%Y-%m-%d"),
            "monto": nueva.monto,
            "categoria": nueva.categoria,
            "descripcion": nueva.descripcion,
            "tipoPago": nueva.tipo_pago,
            "imagen": f"/imagenes/{nueva.imagen}" if nueva.imagen else None,
            "cuotas": nueva.cuotas,
            "interes": nueva.interes,
            "valorCuota": nueva.valor_cuota,
            "totalCredito": nueva.total_credito,
            "tipo": nueva.tipo,
            "repetido": nueva.se_repite,
            "id_usuario": nueva.id_usuario
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@transacciones_bp.route("/<int:id_transaccion>", methods=["PUT"])
def actualizar_transaccion(id_transaccion):
    from datetime import datetime
    import base64
    import os

    data = request.json
    transaccion = db.session.get(Transaccion, id_transaccion)

    if not transaccion:
        return jsonify({"error": "Transacción no encontrada"}), 404

    try:
        transaccion.fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        transaccion.monto = data["monto"]
        transaccion.categoria = data["categoria"]
        transaccion.descripcion = data["descripcion"]
        transaccion.tipo_pago = data["tipoPago"]
        transaccion.cuotas = data.get("cuotas", 1)
        transaccion.interes = data.get("interes", 0)
        transaccion.valor_cuota = data.get("valorCuota")
        transaccion.total_credito = data.get("totalCredito")
        transaccion.tipo = data["tipo"]
        transaccion.se_repite = data.get("repetido", False)

        CARPETA_IMAGENES = os.path.join(os.getcwd(), 'imagenes_transacciones')
        os.makedirs(CARPETA_IMAGENES, exist_ok=True)

        # Eliminar imagen si se indica como null o vacía
        # Procesar imagen
        if "imagen" in data:
            if data["imagen"] == "" or data["imagen"] is None:
                transaccion.imagen = None
            else:
                imagen_bytes = base64.b64decode(data["imagen"])
                if "imagen" in data and isinstance(data["imagen"], str):
                    if data.get("nombre_archivo"):
                        extension = data["nombre_archivo"].split(".")[-1].lower()
                imagen_filename = f"transaccion_{datetime.now().strftime('%Y%m%d%H%M%S')}.{extension}"
                ruta_imagen = os.path.join(CARPETA_IMAGENES, imagen_filename)
                with open(ruta_imagen, 'wb') as f:
                    f.write(imagen_bytes)
                transaccion.imagen = imagen_filename


        db.session.commit()

        return jsonify({"mensaje": "Transacción actualizada correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@transacciones_bp.route("/<int:id_transaccion>/eliminar", methods=["PUT"])
def eliminar_transaccion(id_transaccion):
    transaccion = db.session.get(Transaccion, id_transaccion)
    if not transaccion:
        return jsonify({"error": "Transacción no encontrada"}), 404

    try:
        transaccion.visible = False
        db.session.commit()
        return jsonify({"mensaje": "Transacción eliminada"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@transacciones_bp.route("/<int:id_transaccion>/recuperar", methods=["PUT"])
def recuperar_transaccion(id_transaccion):
    transaccion = db.session.get(Transaccion, id_transaccion)
    if not transaccion:
        return jsonify({"error": "Transacción no encontrada"}), 404

    try:
        transaccion.visible = True
        db.session.commit()
        return jsonify({"mensaje": "Transacción recuperada"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
