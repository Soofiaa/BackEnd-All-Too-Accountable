from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS
import pymysql
from pymysql.cursors import DictCursor  # 👈 Esto es clave

app = Flask(__name__)
CORS(app)

# Configuración para SQLAlchemy (base de datos principal)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:***REMOVED***@localhost/all_too_accountable'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Conexión directa para uso con cursor
def conectar_bd():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="***REMOVED***",
        database="all_too_accountable",
        cursorclass=DictCursor  # ✅ Esto permite acceder a resultados como diccionario
    )
