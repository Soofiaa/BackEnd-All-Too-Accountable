from flask import Blueprint, request, jsonify
from app.models.transaccion import Transaccion
from database import db
from datetime import date, datetime

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

    resultado = []

    # Transacciones normales
    transacciones = Transaccion.query.filter_by(id_usuario=id_usuario).all()
    for t in transacciones:
        try:
            fecha = t.fecha if isinstance(t.fecha, date) else datetime.strptime(str(t.fecha), "%Y-%m-%d").date()
        except Exception as e:
            print(f"⚠️ Error al convertir fecha de transacción ID {t.id_transaccion}: {t.fecha} – {e}")
            continue

        if fecha.month == mes and fecha.year == anio:
            trans_dict = t.to_dict()
            trans_dict["esMensual"] = False
            trans_dict["esProgramado"] = False
            resultado.append(trans_dict)

    '''
    # Gastos mensuales
    gastos_mensuales = GastoMensual.query.filter_by(id_usuario=id_usuario).all()
    for g in gastos_mensuales:
        try:
            fecha_pago = date(anio, mes, g.dia_pago)
        except ValueError:
            continue  # Día inválido para ese mes

        resultado.append({
            "fecha": fecha_pago.isoformat(),
            "monto": g.monto,
            "descripcion": g.descripcion or g.nombre,
            "tipo": "gasto",
            "tipoPago": "automatico",
            "visible": True,
            "id_usuario": id_usuario,
            "id_categoria": g.id_categoria,
            "esMensual": True,
            "esProgramado": False
        })

    # Gastos programados
    pagos_programados = GastoProgramado.query.filter_by(id_usuario=id_usuario, activo=True).all()
    for p in pagos_programados:
        try:
            fecha_trans = p.fecha_transaccion
        except:
            continue

        if fecha_trans.month == mes and fecha_trans.year == anio:
            resultado.append({
                "fecha": fecha_trans.isoformat(),
                "monto": float(p.monto),
                "descripcion": p.descripcion,
                "tipo": "gasto",
                "tipoPago": p.tipo_pago,
                "visible": True,
                "id_usuario": id_usuario,
                "id_categoria": p.id_categoria,
                "esMensual": False,
                "esProgramado": True
            })
    '''
    
    return jsonify(resultado), 200