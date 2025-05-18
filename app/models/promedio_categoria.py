from app import db

class PromedioCategoria(db.Model):
    __tablename__ = 'promedios_categorias'

    id_promedio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    id_categoria = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    monto_total = db.Column(db.Numeric(10, 2), nullable=False)

    def to_dict(self):
        return {
            "id_promedio": self.id_promedio,
            "id_usuario": self.id_usuario,
            "id_categoria": self.id_categoria,
            "mes": self.mes,
            "anio": self.anio,
            "monto_total": float(self.monto_total)
        }
