from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración para MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:***REMOVED***@localhost/all_too_accountable'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
