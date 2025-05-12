from flask import Blueprint, request, jsonify
from app.models.transaccion import Transaccion
from app.models.gasto_mensual import GastoMensual
from app.models.pago_programado import GastoProgramado
from database import db
from datetime import date
from datetime import datetime

transacciones_completas_bp = Blueprint('transacciones_completas', __name__)

@transacciones_completas_bp.route('/api/transacciones_completas', methods=['GET'])
def transacciones_completas():
    id_usuario = request.args.get('id_usuario')
    mes = request.args.get('mes')
    anio = request.args.get('anio')

    if not id_usuario or not mes or not anio:
        return jsonify({'error': 'Faltan parámetros: id_usuario, mes o anio'}), 400

    try:
        mes = int(mes)
        anio = int(anio)
    except ValueError:
        return jsonify({'error': 'Mes y año deben ser números'}), 400

    # TRANSACCIONES NORMALES
    transacciones = Transaccion.query.filter_by(id_usuario=id_usuario).all()
    normales = []
    for t in transacciones:
        if not t.visible:
            continue
        try:
            fecha_obj = t.fecha if isinstance(t.fecha, date) else datetime.strptime(str(t.fecha), "%Y-%m-%d").date()
            if fecha_obj.month == mes and fecha_obj.year == anio:
                normales.append(t.to_dict())
        except Exception as e:
            print(f"⚠️ Error al convertir fecha de transacción ID {t.id_transaccion}: {e}")


    # GASTOS MENSUALES
    gastos_mensuales = GastoMensual.query.filter_by(id_usuario=id_usuario).all()
    hoy = date.today()

    gastos_mensuales_convertidos = []
    for g in gastos_mensuales:
        if g.fecha_creacion.year < anio or (g.fecha_creacion.year == anio and g.fecha_creacion.month <= mes):
            fecha_cobro = date(anio, mes, g.dia_pago)
            if fecha_cobro <= hoy:
                gastos_mensuales_convertidos.append({
                    'id_transaccion': f'gm-{g.id_gasto}',
                    'fecha': fecha_cobro.isoformat(),
                    'monto': g.monto,
                    'categoria': 'Gasto mensual',
                    'descripcion': f'{g.nombre} – {g.descripcion}' if g.descripcion else g.nombre,
                    'tipo': 'gasto',
                    'tipoPago': 'automático',
                    'visible': True,
                    'imagen': None,
                    'protegida': True
                })

    # GASTOS PROGRAMADOS
    gastos_programados = GastoProgramado.query.filter_by(id_usuario=id_usuario, activo=True).all()
    gastos_programados_convertidos = []
    for g in gastos_programados:
        if g.fecha_transaccion.year == anio and g.fecha_transaccion.month == mes:
            gastos_programados_convertidos.append({
                'id_transaccion': f'gp-{g.id_gasto_programado}',
                'fecha': g.fecha_transaccion.isoformat(),  # ✅ corregido
                'monto': g.monto,
                'categoria': 'Gasto programado',
                'descripcion': g.descripcion,
                'tipo': 'gasto',
                'tipoPago': g.tipo_pago,
                'visible': True,
                'imagen': None,
                'protegida': True
            })

    resultado = normales + gastos_mensuales_convertidos + gastos_programados_convertidos
    return jsonify(resultado), 200
