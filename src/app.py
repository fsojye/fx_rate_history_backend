import os

from flask import Flask

from app_context import api, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DB_CONN']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_MASK_SWAGGER'] = False

db.init_app(app)
api.init_app(app)
