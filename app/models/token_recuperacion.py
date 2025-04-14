from database import db
from datetime import datetime

class TokenRecuperacion(db.Model):
    __tablename__ = 'tokens_recuperacion'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    fecha_expiracion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<TokenRecuperacion usuario={self.id_usuario}, token={self.token}>"
