from database import conectar_bd, db
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from app.models.transaccion import Transaccion

class DetallesUsuario:
    def __init__(self, id_usuario, salario, fecha_salario=None):
        self.id_usuario = id_usuario
        self.salario = salario
        self.fecha_salario = fecha_salario

    def guardar(self):
        db = conectar_bd()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO detalles_usuario (id_usuario, salario, fecha_salario) VALUES (%s, %s, %s)",
            (self.id_usuario, self.salario, self.fecha_salario)
        )
        db.commit()
        db.close()

    @staticmethod
    def obtener_por_id(id_usuario):
        db = conectar_bd()
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT salario, fecha_salario 
                FROM detalles_usuario 
                WHERE id_usuario = %s 
                ORDER BY fecha_salario DESC 
                LIMIT 1
            """, (id_usuario,))
            resultado = cursor.fetchone()
            if resultado:
                return {
                    "salario": resultado["salario"],
                    "fecha_salario": resultado["fecha_salario"].isoformat() if resultado["fecha_salario"] else None
                }
            else:
                return {}
        finally:
            db.close()

    @staticmethod
    def obtener_historial(id_usuario):
        db = conectar_bd()
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT id_detalle, salario, fecha_salario 
                FROM detalles_usuario 
                WHERE id_usuario = %s 
                ORDER BY fecha_salario ASC
            """, (id_usuario,))
            return cursor.fetchall()
        finally:
            db.close()

    @staticmethod
    def actualizar_salario(id_usuario, nuevo_salario, fecha_salario):
        db = conectar_bd()
        cursor = db.cursor()
        # Insertar un nuevo registro (NO hacer UPDATE)
        cursor.execute(
            "INSERT INTO detalles_usuario (id_usuario, salario, fecha_salario) VALUES (%s, %s, %s)",
            (id_usuario, nuevo_salario, fecha_salario)
        )
        db.commit()
        db.close()


    @staticmethod
    def insertar_salarios_pasados(id_usuario):
        # 1. Obtener la primera fecha de transacción del usuario
        primera_fecha = db.session.execute(
            db.select(Transaccion.fecha)
            .filter(Transaccion.id_usuario == id_usuario)
            .order_by(Transaccion.fecha.asc())
            .limit(1)
        ).scalar()

        if not primera_fecha:
            print("No hay transacciones para insertar salarios.")
            return

        # Asegura que la fecha sea siempre el primer día del mes
        primer_mes = primera_fecha.replace(day=1) if isinstance(primera_fecha, date) else datetime.combine(primera_fecha, datetime.min.time()).date().replace(day=1)
        hoy = date.today().replace(day=1)

        # 2. Obtener historial de salarios
        historial_salarios = db.session.execute(
            db.select(DetallesUsuario.fecha_salario, DetallesUsuario.salario)
            .filter(DetallesUsuario.id_usuario == id_usuario)
            .order_by(DetallesUsuario.fecha_salario.asc())
        ).all()

        if not historial_salarios:
            print("No hay historial de salarios.")
            return

        # 3. Recorrer desde la primera transacción hasta el mes actual
        mes_actual = primer_mes
        while mes_actual <= hoy:
            # Verifica si ya existe un salario para ese mes
            ya_existe = db.session.execute(
                db.select(Transaccion).where(
                    Transaccion.id_usuario == id_usuario,
                    Transaccion.fecha == mes_actual,
                    Transaccion.descripcion == "Salario mensual",
                    Transaccion.tipo == "ingreso"
                )
            ).scalar()

            if ya_existe:
                mes_actual += relativedelta(months=1)
                mes_actual = mes_actual.replace(day=1)
                continue

            # Buscar el salario vigente en ese mes
            salario_mes = 0
            for fecha_salario, salario in reversed(historial_salarios):
                fecha_solo = fecha_salario if isinstance(fecha_salario, date) else fecha_salario.date()
                if fecha_solo <= mes_actual:
                    salario_mes = float(salario)
                    break

            # Insertar si corresponde
            if salario_mes > 0:
                nueva = Transaccion(
                    fecha=mes_actual,
                    id_categoria=1,
                    descripcion="Salario mensual",
                    tipo_pago="automatico",
                    monto=salario_mes,
                    monto_total=salario_mes,
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
            mes_actual = mes_actual.replace(day=1)

        db.session.commit()