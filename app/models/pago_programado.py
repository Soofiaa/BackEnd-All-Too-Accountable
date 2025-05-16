from app import db

class GastoProgramado(db.Model):
    __tablename__ = 'gastos_programados'

    id_gasto_programado = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    tipo_pago = db.Column(db.Enum('cheque', 'efectivo', 'debito', 'transferencia'), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_emision = db.Column(db.Date, nullable=False)
    dias_cheque = db.Column(db.Integer, nullable=True)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    fecha_transaccion = db.Column(db.Date, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    id_categoria = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id_gasto_programado": self.id_gasto_programado,
            "id_usuario": self.id_usuario,
            "tipo_pago": self.tipo_pago,
            "descripcion": self.descripcion,
            "fecha_emision": str(self.fecha_emision),
            "dias_cheque": self.dias_cheque,
            "monto": float(self.monto),
            "fecha_transaccion": str(self.fecha_transaccion),
            "activo": self.activo,
            "id_categoria": self.id_categoria
        }