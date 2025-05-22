from app import db

class Transaccion(db.Model):
    __tablename__ = 'transacciones'

    id_transaccion = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    
    descripcion = db.Column(db.Text, nullable=False)
    tipo_pago = db.Column(db.Enum('efectivo', 'debito', 'credito', 'transferencia', 'deposito', 'contribucion tarjeta de credito', 'automatico', 'cheque','otro'), nullable=False)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    tipo_pago2 = db.Column(db.Enum('efectivo', 'debito', 'credito', 'transferencia', 'deposito', 'contribucion tarjeta de credito', 'automatico', 'otro'), nullable=True)
    monto2 = db.Column(db.Numeric(12, 2), nullable=True)
    monto_total = db.Column(db.Integer)
    imagen = db.Column(db.String(255))
    cuotas = db.Column(db.Integer, default=1)
    interes = db.Column(db.Numeric(5, 2), default=0)
    valor_cuota = db.Column(db.Numeric(12, 2))
    total_credito = db.Column(db.Numeric(12, 2))
    tipo = db.Column(db.Enum('ingreso', 'gasto'), nullable=False)
    id_usuario = db.Column(db.Integer, nullable=False)
    visible = db.Column(db.Boolean, default=True)
    importada = db.Column(db.Boolean, default=False)
    id_categoria = db.Column(db.Integer)
    id_gasto_mensual = db.Column(db.Integer, nullable=True)
    id_gasto_programado = db.Column(db.Integer, nullable=True)


    def to_dict(self):
        return {
            "id_transaccion": self.id_transaccion,
            "fecha": str(self.fecha),
            "descripcion": self.descripcion,
            "id_categoria": self.id_categoria,
            "tipoPago": self.tipo_pago,
            "monto": self.monto,
            "tipoPago2": self.tipo_pago2,
            "monto2": self.monto2,
            "monto_total": self.monto_total,
            "imagen": f"/imagenes/{self.imagen}" if self.imagen else None,
            "cuotas": self.cuotas,
            "interes": self.interes,
            "valorCuota": self.valor_cuota,
            "totalCredito": self.total_credito,
            "tipo": self.tipo,
            "id_usuario": self.id_usuario,
            "visible": self.visible,
            "importada": self.importada,
            "id_gasto_mensual": self.id_gasto_mensual,
            "id_gasto_programado": self.id_gasto_programado
        }
