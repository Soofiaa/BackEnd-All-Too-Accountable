from database import conectar_bd

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


    @staticmethod
    def obtener_por_id(id_usuario):
        db = conectar_bd()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT salario, fecha_salario FROM detalles_usuario WHERE id_usuario = %s", (id_usuario,))
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
    def actualizar_salario(id_usuario, nuevo_salario, fecha_salario):
        db = conectar_bd()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE detalles_usuario SET salario = %s, fecha_salario = %s WHERE id_usuario = %s",
            (nuevo_salario, fecha_salario, id_usuario)
        )
        db.commit()
