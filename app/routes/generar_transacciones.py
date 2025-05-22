from flask import Blueprint, request, jsonify
from datetime import date
from app.models.gasto_mensual import GastoMensual
from app.models.pago_programado import GastoProgramado
from app.models.transaccion import Transaccion
from app.models.usuario import Usuario
from database import db

generar_transacciones_bp = Blueprint("generar_transacciones", __name__)

@generar_transacciones_bp.route("/api/transacciones/generar_mes_actual", methods=["POST"])
def generar_transacciones_mes_actual():
    try:
        try:
            id_usuario = int(request.args.get("id_usuario"))
        except (ValueError, TypeError):
            return jsonify({"error": "id_usuario inválido"}), 400

        # verificar existencia del usuario
        if not Usuario.query.get(id_usuario):
            return jsonify({"error": "Usuario no encontrado"}), 404

        hoy = date.today()
        anio, mes = hoy.year, hoy.month
        generadas = []

        # GASTOS MENSUALES
        gastos_mensuales = GastoMensual.query.filter_by(id_usuario=id_usuario).all()
        for gasto in gastos_mensuales:
            try:
                fecha_pago = date(anio, mes, gasto.dia_pago)
            except ValueError:
                continue  # Día inválido para ese mes

            ya_existe = Transaccion.query.filter_by(
                id_usuario=id_usuario,
                id_gasto_mensual=gasto.id_gasto,
                fecha=fecha_pago
            ).first()

            if not ya_existe:
                nueva = Transaccion(
                    fecha=fecha_pago,
                    monto=gasto.monto,
                    descripcion=gasto.nombre,
                    tipo_pago="automatico",
                    tipo="gasto",
                    id_usuario=id_usuario,
                    id_categoria=gasto.id_categoria,
                    cuotas=1,
                    interes=0,
                    valor_cuota=0,
                    total_credito=0,
                    tipo_pago2=None,
                    monto2=None,
                    imagen=None,
                    visible=True,
                    id_gasto_mensual=gasto.id_gasto
                )
                db.session.add(nueva)
                generadas.append(f"mensual:{gasto.nombre}")

        # PAGOS PROGRAMADOS
        pagos_programados = GastoProgramado.query.filter_by(id_usuario=id_usuario, activo=True).all()
        for pago in pagos_programados:
            fecha = pago.fecha_transaccion
            if fecha.month == mes and fecha.year == anio:
                ya_existe = Transaccion.query.filter_by(
                    id_usuario=id_usuario,
                    id_gasto_programado=pago.id_gasto_programado,
                    fecha=fecha
                ).first()

                if not ya_existe:
                    nueva = Transaccion(
                        fecha=fecha,
                        monto=pago.monto,
                        descripcion=pago.descripcion,
                        tipo_pago=pago.tipo_pago,
                        tipo="gasto",
                        id_usuario=id_usuario,
                        id_categoria=pago.id_categoria,
                        cuotas=1,
                        interes=0,
                        valor_cuota=0,
                        total_credito=0,
                        tipo_pago2=None,
                        monto2=None,
                        imagen=None,
                        visible=True,
                        id_gasto_programado=pago.id_gasto_programado
                    )
                    db.session.add(nueva)
                    generadas.append(f"programado:{pago.descripcion}")

        db.session.commit()
        return jsonify({
            "mensaje": "Transacciones generadas",
            "transacciones_creadas": generadas
        }), 201

    except Exception as e:
        print("Error al generar transacciones:", e)
        return jsonify({"error": "Ocurrió un error al generar las transacciones"}), 500