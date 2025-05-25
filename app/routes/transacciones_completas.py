from flask import Blueprint, request, jsonify
from app.models.transaccion import Transaccion
from database import db
from datetime import date, datetime
from app.routes.transacciones import insertar_salario_mensual
from app.models.detalle_usuario import DetallesUsuario
from dateutil.relativedelta import relativedelta

transacciones_completas_bp = Blueprint('transacciones_completas', __name__)

@transacciones_completas_bp.route('/api/transacciones_completas', methods=['GET'])
def transacciones_completas():
    try:
        # Obtener y validar parámetros
        id_usuario = request.args.get('id_usuario')
        mes = request.args.get('mes')
        anio = request.args.get('anio')

        if not id_usuario or not mes or not anio:
            return jsonify({'error': 'Faltan parámetros: id_usuario, mes o anio'}), 400

        try:
            id_usuario = int(id_usuario)
            mes = int(mes)
            anio = int(anio)
            if id_usuario <= 0 or not (1 <= mes <= 12) or anio < 2000:
                raise ValueError
        except ValueError:
            return jsonify({'error': 'Parámetros inválidos'}), 400

        # Asegurar inserciones
        insertar_salario_mensual(id_usuario)
        insertar_salarios_pasados(id_usuario)

        normales = []
        eliminadas = []

        transacciones = Transaccion.query.filter_by(id_usuario=id_usuario).all()
        for t in transacciones:
            try:
                if isinstance(t.fecha, str):
                    fecha = datetime.strptime(t.fecha.strip(), "%Y-%m-%d").date()
                elif isinstance(t.fecha, date):
                    fecha = t.fecha
                elif isinstance(t.fecha, datetime):
                    fecha = t.fecha.date()
                else:
                    raise ValueError("Formato de fecha no reconocido")
            except Exception as e:
                print(f"Error al interpretar fecha en transacción ID {t.id_transaccion}: {t.fecha} – {e}")
                continue

            if fecha.month == mes and fecha.year == anio:
                trans_dict = t.to_dict()
                trans_dict["esMensual"] = False
                trans_dict["esProgramado"] = False

                if t.visible is False or t.visible == 0:
                    eliminadas.append(trans_dict)
                else:
                    normales.append(trans_dict)

        return jsonify({
            "normales": normales,
            "mensuales": [],
            "programados": [],
            "eliminadas": eliminadas
        }), 200

    except Exception as e:
        print("Error en /transacciones_completas:", e)
        return jsonify({"error": "Error interno del servidor"}), 500


def insertar_salarios_pasados(id_usuario):
    # 1. Obtener la fecha de la primera transacción registrada
    primera_fecha = db.session.execute(
        db.select(Transaccion.fecha)
        .filter(Transaccion.id_usuario == id_usuario)
        .order_by(Transaccion.fecha.asc())
        .limit(1)
    ).scalar()

    # Asegurar que sea tipo date
    if isinstance(primera_fecha, str):
        primera_fecha = datetime.strptime(primera_fecha.strip(), "%Y-%m-%d").date()
    elif isinstance(primera_fecha, datetime):
        primera_fecha = primera_fecha.date()
    elif not isinstance(primera_fecha, date):
        raise ValueError("Formato de fecha no reconocido")

    primer_mes = primera_fecha.replace(day=1)
    
    if not primera_fecha:
        print("No hay transacciones para insertar salarios.")
        return

    hoy = date.today().replace(day=1)

    # 2. Obtener historial de salarios con fecha
    historial_salarios = DetallesUsuario.obtener_historial(id_usuario)

    if not historial_salarios:
        print("No hay historial de salarios.")
        return

    # 3. Recorrer mes por mes
    mes_actual = primer_mes
    while mes_actual <= hoy:
        # Verificar si ya existe transacción de salario para este mes
        existe = db.session.execute(
            db.select(Transaccion).where(
                Transaccion.id_usuario == id_usuario,
                Transaccion.fecha == mes_actual,
                Transaccion.tipo == "ingreso",
                Transaccion.descripcion == "Salario mensual"
            )
        ).scalar()

        if existe:
            mes_actual += relativedelta(months=1)
            continue

        # Buscar el salario vigente para este mes
        salario_mes = 0
        for registro in reversed(historial_salarios):
            fecha_salario = registro["fecha_salario"]
            salario = registro["salario"]
            if fecha_salario.date() <= mes_actual:
                salario_mes = float(salario)
                break

        if salario_mes > 0:
            nueva = Transaccion(
                fecha=mes_actual.replace(day=1),
                id_categoria=1,  # General
                descripcion="Salario mensual",
                tipo_pago="automatico",
                tipo_pago2=None,
                monto=salario_mes,
                monto2=None,
                monto_total=int(salario_mes),
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
            print(f"Insertado salario: {salario_mes} para {mes_actual}")

        mes_actual += relativedelta(months=1)

    db.session.commit()


def actualizar_salarios_existentes(id_usuario):
    # 1. Obtener historial de salarios
    historial_salarios = db.session.execute(
        db.select(DetallesUsuario.fecha_salario, DetallesUsuario.salario)
        .filter(DetallesUsuario.id_usuario == id_usuario)
        .order_by(DetallesUsuario.fecha_salario.asc())
    ).all()

    if not historial_salarios:
        return

    # 2. Obtener todas las transacciones de salario mensual
    transacciones_salario = db.session.execute(
        db.select(Transaccion).where(
            Transaccion.id_usuario == id_usuario,
            Transaccion.descripcion == "Salario mensual",
            Transaccion.tipo == "ingreso"
        )
    ).scalars().all()

    for t in transacciones_salario:
        salario_correcto = 0

        # Normaliza la fecha de la transacción
        fecha_transaccion = t.fecha
        if isinstance(fecha_transaccion, datetime):
            fecha_transaccion = fecha_transaccion.date()

        for fecha_salario, salario in reversed(historial_salarios):
            if isinstance(fecha_salario, datetime):
                fecha_salario = fecha_salario.date()

            if fecha_salario <= fecha_transaccion:
                salario_correcto = float(salario)
                break

        if salario_correcto > 0 and float(t.monto_total) != salario_correcto:
            t.monto = salario_correcto
            t.monto_total = salario_correcto
            print(f"Actualizado salario en {t.fecha} a {salario_correcto}")

    db.session.commit()