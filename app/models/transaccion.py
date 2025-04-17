from app import db

class Transaccion(db.Model):
    __tablename__ = 'transacciones'

    id_transaccion = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    tipo_pago = db.Column(db.Enum('efectivo', 'debito', 'credito', 'transferencia', 'deposito'), nullable=False)
    imagen = db.Column(db.LargeBinary)
    cuotas = db.Column(db.Integer, default=1)
    interes = db.Column(db.Numeric(5, 2), default=0)
    valor_cuota = db.Column(db.Numeric(12, 2))
    total_credito = db.Column(db.Numeric(12, 2))
    tipo = db.Column(db.Enum('ingreso', 'gasto'), nullable=False)
    se_repite = db.Column(db.Boolean, default=False)
    id_usuario = db.Column(db.Integer, nullable=False)
    visible = db.Column(db.Boolean, default=True)
