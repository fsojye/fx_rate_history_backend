import os

from flask import Flask

import models
from apis import routes
from app_context import api, db, migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DB_CONN']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_MASK_SWAGGER'] = False

db.init_app(app)
migrate.init_app(app, db)
routes.add_resources()
api.init_app(app)
