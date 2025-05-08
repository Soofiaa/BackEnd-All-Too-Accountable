from database import db

class MetaAhorro(db.Model):
    __tablename__ = 'metas_ahorro'

    id_meta = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    fecha_limite = db.Column(db.Date, nullable=False)
    monto_meta = db.Column(db.Integer, nullable=False)
    orden_prioridad = db.Column(db.Integer, nullable=False, default=0)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    def serialize(self):
        return {
            'id_meta': self.id_meta,
            'titulo': self.titulo,
            'fecha_limite': self.fecha_limite.strftime('%d-%m-%Y') if hasattr(self.fecha_limite, 'strftime') else self.fecha_limite,
            'monto_meta': self.monto_meta,
            'orden_prioridad': self.orden_prioridad,
            'id_usuario': self.id_usuario
        }
