from database import db
from datetime import date

class GastoMensual(db.Model):
    __tablename__ = 'gastos_mensuales'

    id_gasto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    monto = db.Column(db.Float, nullable=False)
    dia_pago = db.Column(db.Integer)
    id_usuario = db.Column(db.Integer, nullable=False)
    id_categoria = db.Column(db.Integer)
    fecha_creacion = db.Column(db.Date, nullable=False, default=date.today)
    activo = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id_gasto': self.id_gasto,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'monto': self.monto,
            'dia_pago': self.dia_pago,
            'id_usuario': self.id_usuario,
            'id_categoria': self.id_categoria,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "activo": self.activo
        }