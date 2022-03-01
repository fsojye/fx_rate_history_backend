from flask import Flask

from apis import routes
from app_context import api, db

app = Flask(__name__)
app.config['RESTX_MASK_SWAGGER'] = False

db.init_app(app)
routes.add_resources()
api.init_app(app)
