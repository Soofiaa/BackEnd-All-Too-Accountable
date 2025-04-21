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
        cursor.execute(
            """
            INSERT INTO pagos_pendientes (id_usuario, id_transaccion, descripcion, fecha, cuotas, valorCuota, cuotasPagadas)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (self.id_usuario, self.id_transaccion, self.descripcion, self.fecha, self.cuotas, self.valorCuota, self.cuotasPagadas)
        )
        db.commit()

    @staticmethod
    def obtener_todos():
        db = conectar_bd()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pagos_pendientes WHERE cuotasPagadas < cuotas")
        return cursor.fetchall()

    @staticmethod
    def actualizar_cuotas(id_pago, nuevas_cuotas_pagadas):
        db = conectar_bd()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE pagos_pendientes SET cuotasPagadas = %s WHERE id_pago = %s",
            (nuevas_cuotas_pagadas, id_pago)
        )
        db.commit()
