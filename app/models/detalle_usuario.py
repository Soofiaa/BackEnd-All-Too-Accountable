# models/detalles_usuario.py

from database import conectar_bd

class DetallesUsuario:
    def __init__(self, id_usuario, salario=0, ahorros=0, dia_facturacion=1):
        self.id_usuario = id_usuario
        self.salario = salario
        self.dia_facturacion = dia_facturacion

    def guardar(self):
        db = conectar_bd()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO detalles_usuario (id_usuario, salario, ahorros, dia_facturacion)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salario = VALUES(salario), ahorros = VALUES(ahorros), dia_facturacion = VALUES(dia_facturacion)
        """, (self.id_usuario, self.salario, self.dia_facturacion))
        db.commit()

    @staticmethod
    def obtener_por_id(id_usuario):
        db = conectar_bd()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM detalles_usuario WHERE id_usuario = %s", (id_usuario,))
        return cursor.fetchone()

    @staticmethod
    def actualizar_salario(id_usuario, nuevo_salario):
        db = conectar_bd()
        cursor = db.cursor()
        cursor.execute("UPDATE detalles_usuario SET salario = %s WHERE id_usuario = %s", (nuevo_salario, id_usuario))
        db.commit()