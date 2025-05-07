from app import db

class Transaccion(db.Model):
    __tablename__ = 'transacciones'

    id_transaccion = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    tipo_pago = db.Column(db.Enum('efectivo', 'debito', 'credito', 'transferencia', 'deposito', 'contribucion tarjeta de credito', 'automatico'), nullable=False)
    tipo_pago2 = db.Column(db.Enum('efectivo', 'debito', 'credito', 'transferencia', 'deposito', 'contribucion tarjeta de credito', 'automatico'), nullable=True)
    monto2 = db.Column(db.Numeric(12, 2), nullable=True)

    imagen = db.Column(db.String(255))
    cuotas = db.Column(db.Integer, default=1)
    interes = db.Column(db.Numeric(5, 2), default=0)
    valor_cuota = db.Column(db.Numeric(12, 2))
    total_credito = db.Column(db.Numeric(12, 2))
    tipo = db.Column(db.Enum('ingreso', 'gasto'), nullable=False)
    mes_pago = db.Column(db.String(7))
    id_usuario = db.Column(db.Integer, nullable=False)
    visible = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id_transaccion": self.id_transaccion,
            "fecha": str(self.fecha),
            "monto": self.monto,
            "categoria": self.categoria,
            "descripcion": self.descripcion,
            "tipoPago": self.tipo_pago,
            "tipoPago2": self.tipo_pago2,
            "monto2": self.monto2,
            "imagen": f"/imagenes/{self.imagen}" if self.imagen else None,
            "cuotas": self.cuotas,
            "interes": self.interes,
            "valorCuota": self.valor_cuota,
            "totalCredito": self.total_credito,
            "tipo": self.tipo,
            "mesPago": self.mes_pago,
            "id_usuario": self.id_usuario,
            "visible": self.visible
        }
