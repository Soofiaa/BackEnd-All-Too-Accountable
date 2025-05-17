from flask import Blueprint, request, jsonify, send_file
from database import db
from app.models.categoria import Categoria
from app.models.transaccion import Transaccion
from app.models.pago_programado import GastoProgramado
from app.models.gasto_mensual import GastoMensual
from datetime import date, datetime
from database import conectar_bd
from io import BytesIO
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import pymysql.cursors
import traceback

transacciones_bp = Blueprint("transacciones", __name__)


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
                "tipo": c.tipo,  # 👈 AÑADE ESTO
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
        tipo = data["tipo"]
        monto = float(data["monto"])
        descripcion = data["descripcion"]
        id_usuario = data["id_usuario"]
        id_categoria = data.get("id_categoria")

        # Verificar duplicado
        if tipo_pago in [
            "efectivo", "transferencia", "debito", 
            "contribucion tarjeta de credito", "automatico"
        ]:
            cursor = conectar_bd().cursor()
            if transaccion_ya_existe(cursor, id_usuario, tipo, fecha_pago, monto, descripcion, tipo_pago):
                return jsonify({"error": "Transacción duplicada."}), 409

        # Crear la transacción
        nueva = Transaccion(
            fecha=fecha_pago,
            monto=monto,
            id_categoria=id_categoria,
            descripcion=descripcion,
            tipo_pago=tipo_pago,
            tipo_pago2=tipo_pago2,
            monto2=monto2,
            imagen=imagen_filename,
            cuotas=int(data.get("cuotas", 1)),
            interes=float(data.get("interes", 0)),
            valor_cuota=float(data.get("valorCuota", 0)),
            total_credito=float(data.get("totalCredito", 0)),
            tipo=tipo,
            id_usuario=id_usuario,
            visible=True,
        )

        db.session.add(nueva)
        db.session.commit()

        return jsonify(nueva.to_dict()), 201

    except Exception as e:
        print("❌ Error al guardar transacción:")
        traceback.print_exc()
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
        transaccion.monto = float(data["monto"])
        transaccion.id_categoria = data["id_categoria"]
        transaccion.descripcion = data["descripcion"]
        transaccion.tipo_pago = data["tipoPago"]
        transaccion.tipo_pago2 = data.get("tipoPago2")
        transaccion.monto2 = float(data["monto2"]) if data.get("monto2") else None
        transaccion.cuotas = int(data.get("cuotas", 1))
        transaccion.interes = float(data.get("interes", 0))
        transaccion.valor_cuota = float(data.get("valorCuota", 0))
        transaccion.total_credito = float(data.get("totalCredito", 0))
        transaccion.tipo = data["tipo"]

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

        # Si la transacción proviene de un gasto mensual o programado, actualizamos el gasto original
        if transaccion.id_gasto_mensual:
            gasto = GastoMensual.query.get(transaccion.id_gasto_mensual)
            if gasto:
                gasto.nombre = transaccion.descripcion
                gasto.monto = transaccion.monto
                gasto.id_categoria = transaccion.id_categoria
                db.session.commit()

        if transaccion.id_gasto_programado:
            gasto = GastoProgramado.query.get(transaccion.id_gasto_programado)
            if gasto:
                gasto.descripcion = transaccion.descripcion
                gasto.monto = transaccion.monto
                gasto.id_categoria = transaccion.id_categoria
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


@transacciones_bp.route('/<int:id>/borrar_definitivo', methods=['DELETE', 'OPTIONS'])
def borrar_transaccion_totalmente(id):
    if request.method == "OPTIONS":
        return jsonify({"status": "preflight ok"}), 200

    transaccion = Transaccion.query.get(id)
    if not transaccion:
        return jsonify({"error": "Transacción no encontrada"}), 404

    db.session.delete(transaccion)
    db.session.commit()
    return jsonify({"mensaje": "Transacción eliminada definitivamente"}), 200


@transacciones_bp.route("/programados/<int:id_gasto>/eliminar", methods=["PUT"])
def eliminar_gasto_programado(id_gasto):
    gasto = GastoProgramado.query.get(id_gasto)
    if not gasto:
        return jsonify({"error": "Gasto programado no encontrado"}), 404

    try:
        # Fecha actual
        hoy = date.today()
        anio, mes = hoy.year, hoy.month

        # Buscar transacción asociada (por descripción, monto, fecha del mes actual)
        transaccion = Transaccion.query.filter(
            Transaccion.id_usuario == gasto.id_usuario,
            Transaccion.descripcion == gasto.descripcion,
            Transaccion.monto == gasto.monto,
            db.extract("month", Transaccion.fecha) == mes,
            db.extract("year", Transaccion.fecha) == anio
        ).first()

        if transaccion:
            db.session.delete(transaccion)

        # Desactivar el gasto programado
        gasto.activo = False
        db.session.commit()

        return jsonify({"mensaje": "Gasto programado y transacción eliminados"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@transacciones_bp.route("/mensuales/<int:id_gasto>/eliminar", methods=["PUT"])
def eliminar_gasto_mensual(id_gasto):
    gasto = GastoMensual.query.get(id_gasto)
    if not gasto:
        return jsonify({"error": "Gasto mensual no encontrado"}), 404

    try:
        # Obtener fecha actual
        hoy = date.today()
        anio, mes = hoy.year, hoy.month

        # Construir patrón de descripción (puedes ajustar si quieres exacto)
        descripcion = gasto.nombre

        # Buscar transacción del mismo mes
        transaccion = Transaccion.query.filter(
            Transaccion.id_usuario == gasto.id_usuario,
            Transaccion.descripcion.ilike(f"%{descripcion}%"),
            Transaccion.monto == gasto.monto,
            db.extract("month", Transaccion.fecha) == mes,
            db.extract("year", Transaccion.fecha) == anio
        ).first()

        # Borrar transacción si existe
        if transaccion:
            db.session.delete(transaccion)

        # Desactivar el gasto mensual
        gasto.activo = False
        db.session.commit()

        return jsonify({"mensaje": "Gasto mensual y transacción del mes eliminados"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@transacciones_bp.route("/exportar_mes_actual", methods=["GET"])
def exportar_mes_actual():
    try:
        id_usuario = request.args.get("id_usuario")
        mes = int(request.args.get("mes"))
        anio = int(request.args.get("anio"))
        formato = request.args.get("formato", "excel")

        if not id_usuario or not mes or not anio:
            return jsonify({"error": "Faltan parámetros"}), 400

        # Cargar categorías del usuario (y generales si aplica)
        categorias = db.session.execute(
            db.select(Categoria).where(
                (Categoria.id_usuario == id_usuario) | (Categoria.es_general == True)
            )
        ).scalars().all()
        mapa_categorias = {c.id_categoria: c.nombre for c in categorias}

        # Filtrar transacciones del mes/año
        transacciones = Transaccion.query.filter_by(id_usuario=id_usuario).all()
        transacciones_mes = []
        for t in transacciones:
            fecha = t.fecha
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
            if fecha.month == mes and fecha.year == anio:
                t_dict = t.to_dict()
                t_dict["categoria"] = mapa_categorias.get(t.id_categoria, "Sin categoría")
                transacciones_mes.append(t_dict)

        if not transacciones_mes:
            return jsonify({"error": "No hay transacciones para exportar"}), 404

        columnas_excluir = ["id_transaccion", "imagen", "tipo", "id_usuario", "visible", "importada"]

        # Cálculo resumen
        total_ingresos = sum(float(t["monto"]) for t in transacciones_mes if t["tipo"] == "ingreso")
        total_gastos = sum(float(t["monto"]) for t in transacciones_mes if t["tipo"] == "gasto")
        balance = total_ingresos - total_gastos

        if formato == "excel":
            output = BytesIO()
            df = pd.DataFrame(transacciones_mes)
            df = df.drop(columns=[col for col in columnas_excluir if col in df.columns])

            resumen = {
                "Total ingresos": [total_ingresos],
                "Total gastos": [total_gastos],
                "Balance final": [balance]
            }
            df_resumen = pd.DataFrame(resumen)

            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Transacciones")
                df_resumen.to_excel(writer, index=False, sheet_name="Resumen")

            output.seek(0)
            return send_file(output,
                             download_name=f"transacciones_{mes}-{anio}.xlsx",
                             as_attachment=True,
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        elif formato == "pdf":
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import cm

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph(f"Transacciones de {mes}-{anio}", styles["Title"]))
            elements.append(Spacer(1, 12))

            # Encabezado
            data = [["Fecha", "Monto", "Categoría", "Descripción", "Tipo", "Tipo de pago"]]

            for t in transacciones_mes:
                data.append([
                    t["fecha"],
                    f"${float(t['monto']):,.0f}".replace(",", "."),
                    t["categoria"],
                    t["descripcion"],
                    t["tipo"].capitalize(),
                    t.get("tipoPago", "-")
                ])

            colWidths = [3*cm, 3*cm, 3*cm, 7*cm, 3*cm, 3*cm]
            tabla = Table(data, colWidths=colWidths)
            tabla.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
            ]))
            elements.append(tabla)
            elements.append(Spacer(1, 20))

            # Resumen
            resumen = [
                f"💰 Total ingresos: ${total_ingresos:,.0f}".replace(",", "."),
                f"💸 Total gastos: ${total_gastos:,.0f}".replace(",", "."),
                f"⚖️ Balance final: ${balance:,.0f}".replace(",", ".")
            ]
            for linea in resumen:
                elements.append(Paragraph(linea, styles["Heading4"]))

            doc.build(elements)
            buffer.seek(0)
            return send_file(buffer,
                    download_name=f"transacciones_{mes}-{anio}.pdf",
                    as_attachment=True,
                    mimetype="application/pdf")

        else:
            return jsonify({"error": "Formato no soportado"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        if transaccion_ya_existe(cursor, id_usuario, "gasto", fecha_pago, gasto["monto"], descripcion_completa, "automático", "Gasto mensual"):
            print(f"⛔ Ya existe gasto mensual: {descripcion_completa}")
        else:
            cursor.execute("""
                INSERT INTO transacciones (
                    id_usuario, tipo, fecha, monto, categoria, id_categoria,
                    descripcion, tipo_pago, visible
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
            """, (
                id_usuario,
                "gasto",
                fecha_pago,
                gasto["monto"],
                "Gasto Mensual",
                gasto["id_categoria"],
                descripcion_completa,
                "automático"
            ))
            db.commit()
            

def insertar_gastos_programados_como_transacciones(id_usuario):
    print("🛠️ Ejecutando función insertar_gastos_programados_como_transacciones() para usuario:", id_usuario)
    
    db_conn = conectar_bd()
    cursor = db_conn.cursor(pymysql.cursors.DictCursor)

    hoy = datetime.now()
    mes_actual = hoy.month
    anio_actual = hoy.year

    cursor.execute("""
        SELECT * FROM gastos_programados
        WHERE id_usuario = %s AND activo = TRUE
    """, (id_usuario,))
    gastos = cursor.fetchall()

    print(f"🔍 {len(gastos)} gastos programados encontrados")

    for gasto in gastos:
        fecha_raw = gasto.get("fecha_transaccion")

        if not fecha_raw:
            print(f"⚠️ Gasto sin fecha_transaccion: {gasto['descripcion']}")
            continue

        # Convertir fecha_transaccion a tipo date
        if isinstance(fecha_raw, str):
            try:
                fecha = datetime.strptime(fecha_raw, "%Y-%m-%d").date()
            except ValueError:
                try:
                    fecha = datetime.strptime(fecha_raw, "%Y-%m-%d %H:%M:%S").date()
                except Exception:
                    print(f"❌ Fecha inválida: {fecha_raw}")
                    continue
        elif isinstance(fecha_raw, datetime):
            fecha = fecha_raw.date()
        elif isinstance(fecha_raw, date):
            fecha = fecha_raw
        else:
            print(f"❌ Formato no soportado para fecha: {fecha_raw}")
            continue

        print(f"📅 Evaluando gasto '{gasto['descripcion']}' con fecha {fecha}")

        if fecha.month == mes_actual and fecha.year == anio_actual:
            print(f"✅ Gasto aplica para el mes actual ({mes_actual}-{anio_actual})")

            # Verificar si ya existe esa transacción para ese gasto programado
            cursor.execute("""
                SELECT 1 FROM transacciones
                WHERE id_usuario = %s AND tipo = %s AND fecha = %s AND monto = %s AND descripcion = %s AND tipo_pago = %s
            """, (
                id_usuario,
                "gasto",  # o variable si estás insertando ingresos también
                fecha,
                gasto["monto"],
                gasto["descripcion"],
                gasto["tipo_pago"]
            ))
            ya_existe = cursor.fetchone()

            if ya_existe:
                print("⛔ Ya existe una transacción exactamente igual, no se insertará.")
            else:
                print("📥 Insertando gasto programado como transacción real...")
                cursor.execute("""
                    INSERT INTO transacciones (
                        id_usuario, tipo, fecha, monto, id_categoria,
                        descripcion, tipo_pago, visible, importada, id_gasto_programado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, 1, 1, %s)
                """, (
                    id_usuario,
                    "gasto",
                    fecha,
                    gasto["monto"],
                    "Gasto Programado",
                    gasto.get("id_categoria"),  # ✅ insertamos el ID real
                    gasto["descripcion"],
                    gasto["tipo_pago"],
                    gasto["id_gasto_programado"]
                ))
                db_conn.commit()
                print("✅ Insertado con éxito.")
        else:
            print("⏩ Gasto no corresponde al mes actual, se omite.")


def transaccion_ya_existe(cursor, id_usuario, tipo, fecha, monto, descripcion, tipo_pago):
    cursor.execute("""
        SELECT 1 FROM transacciones
        WHERE id_usuario = %s AND tipo = %s AND fecha = %s
        AND monto = %s AND descripcion = %s AND tipo_pago = %s
    """, (
        id_usuario, tipo, fecha, monto, descripcion, tipo_pago
    ))
    return cursor.fetchone() is not None
