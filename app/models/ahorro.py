from database import db
from datetime import date

class MovimientoAhorro(db.Model):
    __tablename__ = 'movimientos_ahorro'

    id_movimiento = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.Enum('agregar', 'quitar'), nullable=False)
    monto = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id_movimiento": self.id_movimiento,
            "id_usuario": self.id_usuario,
            "fecha": self.fecha.isoformat(),
            "tipo": self.tipo,
            "monto": self.monto
        }

    @staticmethod
    def crear_predeterminado_si_no_existe(id_usuario):
        existe = MovimientoAhorro.query.filter_by(id_usuario=id_usuario).first()
        if not existe:
            nuevo = MovimientoAhorro(
                id_usuario=id_usuario,
                fecha=date.today(),
                tipo='agregar',
                monto=0
            )
            db.session.add(nuevo)
            db.session.commit()
