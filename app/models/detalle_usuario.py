# models/detalles_usuario.py

from database import conectar_bd

class DetallesUsuario:
    def __init__(self, id_usuario, salario, ahorros, dia_facturacion):
        self.id_usuario = id_usuario
        self.salario = salario
        self.dia_facturacion = dia_facturacion


    def guardar(self):
        db = conectar_bd()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO detalles_usuario (id_usuario, salario, dia_facturacion) VALUES (%s, %s, %s)",
            (self.id_usuario, self.salario, self.dia_facturacion)
        )
        db.commit()


    @staticmethod
    def obtener_por_id(id_usuario):
        db = conectar_bd()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT salario, dia_facturacion FROM detalles_usuario WHERE id_usuario = %s", (id_usuario,))
            resultado = cursor.fetchone()
            if resultado:
                return {
                    "salario": resultado["salario"],
                    "dia_facturacion": resultado["dia_facturacion"]
                }
            else:
                return {}  # o None si prefieres manejarlo así en el frontend
        finally:
            db.close()


    @staticmethod
    def actualizar_salario(id_usuario, nuevo_salario):
        db = conectar_bd()
        cursor = db.cursor()
        cursor.execute("UPDATE detalles_usuario SET salario = %s WHERE id_usuario = %s", (nuevo_salario, id_usuario))
        db.commit()