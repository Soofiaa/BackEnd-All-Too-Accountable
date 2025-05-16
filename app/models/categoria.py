from app import db

class Categoria(db.Model):
    __tablename__ = 'categorias'

    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # Ingreso / Gasto / Ambos
    id_usuario = db.Column(db.Integer, nullable=True)
    es_general = db.Column(db.Boolean, default=False)
    monto_limite = db.Column(db.Float, default=0)

    def to_dict(self):
        return {
            "id_categoria": self.id_categoria,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "id_usuario": self.id_usuario,
            "es_general": self.es_general,
            "monto_limite": self.monto_limite
        }
