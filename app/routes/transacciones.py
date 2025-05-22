from flask import Blueprint, request, jsonify, send_file
from database import db
from app.models.categoria import Categoria
from app.models.transaccion import Transaccion
from app.models.pago_programado import GastoProgramado
from app.models.gasto_mensual import GastoMensual
from app.models.detalle_usuario import DetallesUsuario
from datetime import date, datetime
from database import conectar_bd
from io import BytesIO
import pandas as pd
import traceback
from datetime import datetime
import base64
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_from_directory

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
                "tipo": c.tipo,
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
    data = request.json
    CARPETA_IMAGENES = os.path.join(os.getcwd(), 'imagenes_transacciones')
    os.makedirs(CARPETA_IMAGENES, exist_ok=True)

    try:
        # Validaciones
        try:
            fecha_pago = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        except:
            return jsonify({"error": "Fecha inválida"}), 400

        try:
            monto = float(data["monto"])
            if monto <= 0:
                raise ValueError
        except:
            return jsonify({"error": "Monto inválido"}), 400

        descripcion = data.get("descripcion", "").strip()
        if not descripcion or len(descripcion) > 100:
            return jsonify({"error": "Descripción inválida"}), 400

        try:
            id_usuario = int(data["id_usuario"])
            if id_usuario <= 0:
                raise ValueError
        except:
            return jsonify({"error": "id_usuario inválido"}), 400

        tipo_pago = data.get("tipoPago", "").strip()
        if tipo_pago not in ["efectivo", "transferencia", "debito", "credito", "automatico", "contribucion tarjeta de credito"]:
            return jsonify({"error": "Tipo de pago inválido"}), 400

        tipo = data.get("tipo", "").strip()
        if tipo not in ["ingreso", "gasto"]:
            return jsonify({"error": "Tipo inválido"}), 400

        tipo_pago2 = data.get("tipoPago2")
        monto2 = float(data["monto2"]) if data.get("monto2") else None
        id_categoria = data.get("id_categoria")

        # Validación de duplicado
        if tipo_pago in ["efectivo", "transferencia", "debito", "contribucion tarjeta de credito", "automatico"]:
            cursor = conectar_bd().cursor()
            if transaccion_ya_existe(cursor, id_usuario, tipo, fecha_pago, monto, descripcion, tipo_pago):
                return jsonify({"error": "Transacción duplicada."}), 409

        # Guardar imagen si viene
        imagen_filename = None
        if data.get("imagen"):
            imagen_bytes = base64.b64decode(data["imagen"])
            imagen_filename = f"transaccion_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            ruta_imagen = os.path.join(CARPETA_IMAGENES, imagen_filename)
            with open(ruta_imagen, 'wb') as f:
                f.write(imagen_bytes)

        monto_total = int(monto + (monto2 if monto2 else 0))

        nueva = Transaccion(
            fecha=fecha_pago,
            id_categoria=id_categoria,
            descripcion=descripcion,
            tipo_pago=tipo_pago,
            monto=monto,
            tipo_pago2=tipo_pago2,
            monto2=monto2,
            monto_total=monto_total,
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
        print("Error al guardar transacción:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400


@transacciones_bp.route("/<int:id_transaccion>", methods=["PUT"])
def actualizar_transaccion(id_transaccion):
    data = request.json
    transaccion = db.session.get(Transaccion, id_transaccion)

    if not transaccion:
        return jsonify({"error": "Transacción no encontrada"}), 404

    try:
        try:
            transaccion.fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        except:
            return jsonify({"error": "Fecha inválida"}), 400

        try:
            transaccion.monto = float(data["monto"])
            if transaccion.monto <= 0:
                raise ValueError
        except:
            return jsonify({"error": "Monto inválido"}), 400

        descripcion = data.get("descripcion", "").strip()
        if not descripcion or len(descripcion) > 100:
            return jsonify({"error": "Descripción inválida"}), 400
        transaccion.descripcion = descripcion

        transaccion.id_categoria = data["id_categoria"]

        tipo = data.get("tipo", "").strip()
        if tipo not in ["ingreso", "gasto"]:
            return jsonify({"error": "Tipo inválido"}), 400
        transaccion.tipo = tipo

        tipo_pago = data.get("tipoPago", "").strip()
        if tipo_pago not in ["efectivo", "transferencia", "debito", "credito", "automatico", "contribucion tarjeta de credito"]:
            return jsonify({"error": "Tipo de pago inválido"}), 400
        transaccion.tipo_pago = tipo_pago

        transaccion.tipo_pago2 = data.get("tipoPago2")
        transaccion.monto2 = float(data["monto2"]) if data.get("monto2") else None
        transaccion.cuotas = int(data.get("cuotas", 1))
        transaccion.monto_total = int(transaccion.monto + (transaccion.monto2 if transaccion.monto2 else 0))
        transaccion.interes = float(data.get("interes", 0))
        transaccion.valor_cuota = float(data.get("valorCuota", 0))
        transaccion.total_credito = float(data.get("totalCredito", 0))

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

        # Si la transacción proviene de un gasto recurrente, actualiza origen
        hoy = date.today()
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

        categorias = db.session.execute(
            db.select(Categoria).where(
                (Categoria.id_usuario == id_usuario) | (Categoria.es_general == True)
            )
        ).scalars().all()
        mapa_categorias = {c.id_categoria: c.nombre for c in categorias}

        detalle = DetallesUsuario.obtener_por_id(id_usuario)
        monto_salario = float(detalle["salario"]) if detalle and detalle.get("salario") else 0

        transacciones = Transaccion.query.filter_by(id_usuario=id_usuario).all()
        transacciones_mes = []
        for t in transacciones:
            fecha = t.fecha
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
            if fecha.month == mes and fecha.year == anio:
                if t.visible is False or t.visible == 0:
                    continue
                t_dict = t.to_dict()
                t_dict["categoria"] = mapa_categorias.get(t.id_categoria, "Sin categoría")
                transacciones_mes.append(t_dict)

        if not transacciones_mes:
            return jsonify({"error": "No hay transacciones para exportar"}), 404

        columnas_excluir = [
            "id_transaccion", "imagen", "id_usuario", "visible",
            "importada", "id_gasto_mensual", "id_gasto_programado", "id_categoria",
            "cuotas", "interes", "valorCuota", "totalCredito"
        ]

        total_ingresos = sum(float(t["monto_total"] if t.get("monto_total") else t["monto"]) for t in transacciones_mes if t["tipo"] == "ingreso")
        total_gastos = sum(float(t["monto_total"] if t.get("monto_total") else t["monto"]) for t in transacciones_mes if t["tipo"] == "gasto")
        balance = total_ingresos - total_gastos

        if formato == "excel":
            output = BytesIO()
            transacciones_mes.sort(key=lambda t: t["fecha"])
            df = pd.DataFrame(transacciones_mes)
            df = df.drop(columns=[col for col in columnas_excluir if col in df.columns])
            
            # Asegurar que monto2 se vea como entero
            if "monto2" in df.columns:
                df["monto2"] = df["monto2"].fillna(0).astype(int)

            columnas_deseadas = ["fecha", "tipo", "monto", "tipoPago", "descripcion", "categoria"]
            otras_columnas = [col for col in df.columns if col not in columnas_deseadas]
            orden_final = columnas_deseadas + otras_columnas
            df = df[orden_final]

            resumen = []
            if monto_salario > 0:
                resumen.append(["Salario", f"${monto_salario:,.0f}".replace(",", ".")])

            resumen.extend([
                ["Total ingresos", f"${total_ingresos:,.0f}".replace(",", ".")],
                ["Total gastos", f"${total_gastos:,.0f}".replace(",", ".")],
                ["Balance final", f"${balance:,.0f}".replace(",", ".")]
            ])

            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Transacciones")
                hoja = writer.sheets["Transacciones"]
                startrow = len(df) + 3
                for i, fila in enumerate(resumen):
                    hoja.cell(row=startrow + i + 1, column=1, value=fila[0])
                    hoja.cell(row=startrow + i + 1, column=2, value=fila[1])

            output.seek(0)
            return send_file(
                output,
                download_name=f"transacciones_{mes}-{anio}.xlsx",
                as_attachment=True,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        elif formato == "pdf":
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))

            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph(f"Transacciones de {mes}-{anio}", styles["Title"]))
            elements.append(Spacer(1, 12))

            data = [["Fecha", "Tipo", "Monto", "Tipo de pago", "Descripción", "Categoría", "Tipo pago 2", "Monto 2", "Monto total"]]
            for t in sorted(transacciones_mes, key=lambda x: x["fecha"]):
                data.append([
                    t["fecha"],
                    t["tipo"].capitalize(),
                    f"${float(t['monto']):,.0f}".replace(",", "."),
                    t.get("tipoPago", "-"),
                    Paragraph(t["descripcion"], styles["Normal"]),
                    t["categoria"],
                    t.get("tipoPago2", "-"),
                    f"${int(t['monto2'])}" if t.get("monto2") else "-",
                    f"${int(t['monto_total'])}" if t.get("monto_total") else "-"
                ])

            tabla = Table(data)
            tabla._argW = [70, 45, 60, 70, 140, 75, 75, 55, 65]
            tabla.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),  # título de columnas
                ("FONTSIZE", (0, 1), (-1, -1), 8),  # contenido
            ]))
            elements.append(tabla)
            elements.append(Spacer(1, 20))

            resumen = []
            if monto_salario > 0:
                resumen.append(f"Salario: ${monto_salario:,.0f}".replace(",", "."))
            resumen.extend([
                f"Total ingresos: ${total_ingresos:,.0f}".replace(",", "."),
                f"Total gastos: ${total_gastos:,.0f}".replace(",", "."),
                f"Balance final: ${balance:,.0f}".replace(",", ".")
            ])
            for linea in resumen:
                elements.append(Paragraph(linea, styles["Heading4"]))

            doc.build(elements)
            buffer.seek(0)
            return send_file(
                buffer,
                download_name=f"transacciones_{mes}-{anio}.pdf",
                as_attachment=True,
                mimetype="application/pdf"
            )

        else:
            return jsonify({"error": "Formato no soportado"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def transaccion_ya_existe(cursor, id_usuario, tipo, fecha, monto, descripcion, tipo_pago):
    cursor.execute("""
        SELECT 1 FROM transacciones
        WHERE id_usuario = %s AND tipo = %s AND fecha = %s
        AND monto = %s AND descripcion = %s AND tipo_pago = %s
    """, (
        id_usuario, tipo, fecha, monto, descripcion, tipo_pago
    ))
    return cursor.fetchone() is not None


@transacciones_bp.route('/imagenes/<nombre>')
def obtener_imagen(nombre):
    ruta = os.path.join(os.getcwd(), 'imagenes_transacciones')
    return send_from_directory(ruta, nombre)


def insertar_salario_mensual(id_usuario):
    hoy = date.today()
    primer_dia_mes = date(hoy.year, hoy.month, 1)

    # 🔍 Buscar transacción de salario mensual sin importar visible
    ya_existe = db.session.execute(
        db.select(Transaccion).where(
            Transaccion.id_usuario == id_usuario,
            Transaccion.fecha == primer_dia_mes,
            Transaccion.tipo == "ingreso",
            Transaccion.descripcion == "Salario mensual"
        )
    ).scalars().first()

    if ya_existe:
        print("Ya existe salario mensual. No se inserta.")
        return

    print("NO existe salario mensual. Procediendo a insertar...")

    # Obtener salario actual del usuario
    detalle = DetallesUsuario.obtener_por_id(id_usuario)
    if not detalle:
        print("No se encontró detalle del usuario.")
        return

    salario = float(detalle.get("salario", 0))
    print("Salario detectado:", salario)

    if salario <= 0:
        print("Salario es 0 o menor. No se inserta transacción.")
        return

    # Crear la transacción
    nueva = Transaccion(
        fecha=primer_dia_mes,
        id_categoria=1,  # General
        descripcion="Salario mensual",
        tipo_pago="automatico",
        tipo_pago2=None,
        monto=salario,
        monto2=None,
        monto_total=int(salario),
        imagen=None,
        cuotas=1,
        interes=0,
        valor_cuota=0,
        total_credito=0,
        tipo="ingreso",
        id_usuario=id_usuario,
        visible=True
    )

    db.session.add(nueva)
    db.session.commit()
    print("Salario mensual insertado exitosamente.")