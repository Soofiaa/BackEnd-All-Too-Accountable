from app.database import db

class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # ingreso o gasto
    visible = db.Column(db.Boolean, default=True)