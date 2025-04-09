from database import db

class Transaccion(db.Model):
    __tablename__ = 'transacciones'

    id_transaccion = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date)
    monto = db.Column(db.Float)
    categoria = db.Column(db.String(100))
    descripcion = db.Column(db.String(255))
    tipo_pago = db.Column(db.String(50))
    imagen = db.Column(db.String(255))
    cuotas = db.Column(db.Integer)
    interes = db.Column(db.Float)
    valor_cuota = db.Column(db.Float)
    total_credito = db.Column(db.Float)
    tipo = db.Column(db.String(20))
    se_repite = db.Column(db.Boolean)
    id_usuario = db.Column(db.Integer)
    visible = db.Column(db.Boolean, default=True)  # <--- ASEGÚRATE DE TENER ESTA LÍNEA
