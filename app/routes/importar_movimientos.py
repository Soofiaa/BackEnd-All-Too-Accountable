from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from werkzeug.utils import secure_filename
import pandas as pd
import os
from app.models.transaccion import Transaccion, db
from app.models.categoria import Categoria
import re
from datetime import datetime
from app.models.usuario import Usuario

importar_bp = Blueprint('importar', __name__)

@importar_bp.route("/api/importar_movimientos", methods=["POST"])
def importar_movimientos():
    archivo = request.files.get("archivo")
    
    nombre_archivo = secure_filename(archivo.filename).lower()
    if not (nombre_archivo.endswith(".csv") or nombre_archivo.endswith(".xlsx")):
        return jsonify({"error": "Solo se permiten archivos .csv o .xlsx"}), 400

    id_usuario = request.form.get("id_usuario")

    if not Usuario.query.get(id_usuario):
        return jsonify({"error": "El usuario no existe"}), 404

    cat_general = Categoria.query.filter(
        Categoria.nombre == "General",
        or_(
            Categoria.id_usuario == int(id_usuario),
            Categoria.id_usuario == None
        )
    ).first()
    
    if not cat_general:
        return jsonify({"error": "No se encontró la categoría 'General'"}), 500

    id_general = cat_general.id_categoria if cat_general else None

    if not archivo or not id_usuario:
        return jsonify({"error": "Falta archivo o id_usuario"}), 400

    try:
        # Guardar temporalmente
        nombre_archivo = secure_filename(archivo.filename)
        ruta_temporal = os.path.join("uploads", nombre_archivo)
        archivo.save(ruta_temporal)

        # Leer con pandas
        df = pd.read_excel(ruta_temporal, header=2) if archivo.filename.endswith(".xlsx") else pd.read_csv(ruta_temporal)
        
        if df.empty:
            return jsonify({"error": "El archivo está vacío"}), 400

        # Validar columnas esperadas
        # Normalizamos nombres de columnas
        def normalizar_columna(col):
            col = str(col).strip().lower()
            col = re.sub(r"\s*\(.*?\)", "", col)  # elimina paréntesis y espacios antes
            col = col.replace(" ", "_").replace("$", "").replace("₽", "").strip("_")
            return col

        df.columns = [normalizar_columna(col) for col in df.columns]

        # Verificamos existencia
        columnas_obligatorias = ["fecha", "detalle", "monto_cargo", "monto_abono"]
        for col in columnas_obligatorias:
            if col not in df.columns:
                return jsonify({"error": f"Falta la columna '{col}' en el archivo."}), 400


        transacciones_agregadas = 0

        for _, fila in df.iterrows():
            fecha_raw = str(fila.get("fecha", "")).strip()

            try:
                # Intenta convertir desde formato "DD-MM-YYYY" a datetime
                fecha = datetime.strptime(fecha_raw, "%d-%m-%Y").date()
            except ValueError:
                # Si falla, intenta como "YYYY-MM-DD"
                try:
                    fecha = datetime.strptime(fecha_raw, "%Y-%m-%d").date()
                except Exception as e:
                    print(f"Fecha inválida: {fecha_raw} – {e}")
                    continue

            detalle = str(fila.get("detalle", "")).strip()
            cargo = fila.get("monto_cargo", 0)
            abono = fila.get("monto_abono", 0)

            if pd.isna(fecha) or pd.isna(detalle):
                continue

            monto = cargo if not pd.isna(cargo) and cargo else abono
            tipo = "gasto" if not pd.isna(cargo) and cargo else "ingreso"

            if not monto or pd.isna(monto):
                continue

            descripcion_lower = detalle.lower()
            if "transf" in descripcion_lower:
                tipo_pago = "transferencia"
            else:
                tipo_pago = "otro"

            # Verificar si ya existe la misma transacción
            ya_existe = Transaccion.query.filter_by(
                id_usuario=id_usuario,
                fecha=fecha,
                descripcion=detalle,
                monto=monto,
                tipo=tipo,
                tipo_pago=tipo_pago
            ).first()

            if ya_existe:
                print(f"Transacción duplicada ignorada: {detalle} – {fecha}")
                continue
            
            nueva = Transaccion(
                id_usuario=id_usuario,
                fecha=fecha,
                descripcion=detalle,
                monto=monto,
                tipo=tipo,
                tipo_pago=tipo_pago,
                id_categoria=id_general,
                visible=True,
                importada=True
            )
            db.session.add(nueva)
            transacciones_agregadas += 1

        db.session.commit()
        os.remove(ruta_temporal)

        return jsonify({"mensaje": f"{transacciones_agregadas} transacciones importadas con éxito."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
