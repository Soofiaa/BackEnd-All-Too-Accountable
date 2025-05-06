from database import conectar_bd, db

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)


    @staticmethod
    def obtener_por_id(id_usuario):
        db = conectar_bd()
        cursor = db.cursor()
        cursor.execute("SELECT nombre_usuario FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        resultado = cursor.fetchone()
        db.close()
        if resultado:
            return {"nombre_usuario": resultado[0]}
        return None
