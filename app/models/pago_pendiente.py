from database import conectar_bd

class PagoPendiente:
    def __init__(self, id_usuario, id_transaccion, descripcion, fecha, cuotas, valorCuota, cuotasPagadas=0):
        self.id_usuario = id_usuario
        self.id_transaccion = id_transaccion
        self.descripcion = descripcion
        self.fecha = fecha
        self.cuotas = cuotas
        self.valorCuota = valorCuota
        self.cuotasPagadas = cuotasPagadas

    def guardar(self):
        db = conectar_bd()
        cursor = db.cursor()
        try:
            print("💾 Insertando con:", self.__dict__)
            cursor.execute(
                "INSERT INTO pagos_pendientes (id_usuario, id_transaccion, descripcion, fecha, cuotas, cuotasPagadas, valorCuota) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    int(self.id_usuario),
                    int(self.id_transaccion),
                    str(self.descripcion),
                    self.fecha,  # ya es tipo date
                    int(self.cuotas),
                    int(0),
                    float(self.valorCuota)
                )
            )
            db.commit()
            print("✅ Pago pendiente insertado correctamente")
        except Exception as e:
            import traceback
            traceback.print_exc()

    @staticmethod
    def obtener_por_usuario(id_usuario):
        print("🧪 Obteniendo pagos para usuario:", id_usuario)
        db = conectar_bd()
        cursor = db.cursor()

        try:
            cursor.execute("""
                SELECT p.id_pago, p.id_usuario, p.id_transaccion, p.descripcion, p.fecha, p.cuotas, 
                    p.cuotasPagadas, p.valorCuota
                FROM pagos_pendientes p
                JOIN transacciones t ON p.id_transaccion = t.id_transaccion
                WHERE p.id_usuario = %s
                AND p.cuotasPagadas < p.cuotas
                AND t.visible = 1
            """, (id_usuario,))

            filas = cursor.fetchall()
            print("✅ Resultados reales:", filas)
            return filas

        except Exception as e:
            import traceback
            traceback.print_exc()
            return []


    @staticmethod
    def actualizar_cuotas(id_pago, nuevas_cuotas_pagadas):
        db = conectar_bd()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE pagos_pendientes SET cuotasPagadas = %s WHERE id_pago = %s",
            (nuevas_cuotas_pagadas, id_pago)
        )
        db.commit()
