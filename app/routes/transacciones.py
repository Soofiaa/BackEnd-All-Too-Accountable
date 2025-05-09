import os
from flask import Blueprint, request, jsonify
from database import db
from app.models.categoria import Categoria
from app.models.transaccion import Transaccion
from datetime import datetime
import base64
from database import conectar_bd

transacciones_bp = Blueprint("transacciones", __name__)

def insertar_gastos_mensuales_como_transacciones(id_usuario):
    db = conectar_bd()
    cursor = db.cursor()

    hoy = datetime.now()
    mes_actual = hoy.month
    anio_actual = hoy.year

    # Traer todos los gastos mensuales del usuario
    cursor.execute("""
        SELECT * FROM gastos_mensuales
        WHERE id_usuario = %s
    """, (id_usuario,))
    gastos = cursor.fetchall()

    for gasto in gastos:
        fecha_pago = f"{anio_actual}-{str(mes_actual).zfill(2)}-{str(gasto['dia_pago']).zfill(2)}"

        # Combinar nombre + descripción
        descripcion_completa = f"{gasto['nombre']} - {gasto['descripcion']}"

        # Verificar si ya existe esa transacción para ese mes
        cursor.execute("""
            SELECT * FROM transacciones
            WHERE id_usuario = %s AND descripcion = %s AND fecha = %s
        """, (id_usuario, descripcion_completa, fecha_pago))
        ya_existe = cursor.fetchone()

        if not ya_existe:
            cursor.execute("""
                INSERT INTO transacciones (
                    id_usuario, tipo, fecha, monto, categoria,
                    descripcion, tipo_pago, visible
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
            """, (
                id_usuario,
                "gasto",
                fecha_pago,
                gasto["monto"],
                "Gasto mensual",
                descripcion_completa,
                "automático"
            ))
            db.commit()


@transacciones_bp.route('/categorias/<int:id_usuario>', methods=['GET'])
def obtener_categorias_transacciones(id_usuario):
    try:
        categorias = db.session.execute(
            db.select(Categoria).where(
                (Categoria.id_usuario == id_usuario) | (Categoria.es_general == True)
            )
        ).scalars().all()

        resultado = [
            {
                "nombre": c.nombre,
                "monto_limite": float(c.monto_limite or 0)
            }
            for c in categorias
        ]

        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@transacciones_bp.route('/<int:id_usuario>', methods=['GET'])
def obtener_transacciones_usuario(id_usuario):
    transacciones = db.session.execute(
        db.select(Transaccion).where(
            (Transaccion.id_usuario == id_usuario) &
            (Transaccion.visible == True)
        )
    ).scalars().all()

    return jsonify([t.to_dict() for t in transacciones])


@transacciones_bp.route('/<int:id_usuario>/todas', methods=['GET'])
def obtener_todas_transacciones_usuario(id_usuario):
    insertar_gastos_mensuales_como_transacciones(id_usuario)

    transacciones = db.session.execute(
        db.select(Transaccion).where(
            Transaccion.id_usuario == id_usuario
        )
    ).scalars().all()

    return jsonify([t.to_dict() for t in transacciones])


@transacciones_bp.route("", methods=["POST"])
def crear_transaccion():
    from datetime import datetime
    import base64
    import os

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

        fecha_pago = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        tipo_pago = data["tipoPago"]
        
        tipo_pago2 = data.get("tipoPago2")
        monto2 = float(data["monto2"]) if data.get("monto2") else None

        # Calcular mesPago automáticamente
        if tipo_pago in [
            "efectivo", "transferencia", "debito", 
            "contribucion tarjeta de credito", "automatico"
        ]:
            mes_pago = fecha_pago.strftime("%Y-%m")  # ejemplo: "2025-05"
        else:
            mes_pago = data.get("mesPago")

        nueva = Transaccion(
            fecha=fecha_pago,
            monto=float(data["monto"]),
            categoria=data["categoria"],
            descripcion=data["descripcion"],
            tipo_pago=tipo_pago,
            tipo_pago2=tipo_pago2,                  
            monto2=monto2,                          
            imagen=imagen_filename,
            cuotas=int(data.get("cuotas", 1)),
            interes=float(data.get("interes", 0)),
            valor_cuota=float(data.get("valorCuota", 0)),
            total_credito=float(data.get("totalCredito", 0)),
            tipo=data["tipo"],
            id_usuario=data["id_usuario"],
            visible=True,
            mes_pago=mes_pago
        )

        db.session.add(nueva)
        db.session.commit()

        return jsonify(nueva.to_dict()), 201

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

        # 🔁 NUEVOS CAMPOS
        transaccion.tipo_pago2 = data.get("tipoPago2")
        transaccion.monto2 = float(data["monto2"]) if data.get("monto2") else None

        transaccion.cuotas = data.get("cuotas", 1)
        transaccion.interes = data.get("interes", 0)
        transaccion.valor_cuota = data.get("valorCuota")
        transaccion.total_credito = data.get("totalCredito")
        transaccion.tipo = data["tipo"]

        # Actualizar mesPago si corresponde
        if transaccion.tipo_pago in ["efectivo", "transferencia", "debito", "contribucion tarjeta de credito"]:
            transaccion.mes_pago = transaccion.fecha.strftime("%Y-%m")
        else:
            transaccion.mes_pago = data.get("mesPago")

        # Procesar imagen si viene
        CARPETA_IMAGENES = os.path.join(os.getcwd(), 'imagenes_transacciones')
        os.makedirs(CARPETA_IMAGENES, exist_ok=True)

        if "imagen" in data:
            if data["imagen"] == "" or data["imagen"] is None:
                transaccion.imagen = None
            else:
                imagen_bytes = base64.b64decode(data["imagen"])
                extension = data.get("nombre_archivo", "jpg").split(".")[-1].lower()
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
