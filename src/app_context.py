import os
from distutils.util import strtobool

from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate(
    compare_type=True,
    compare_server_default=True
)
ma = Marshmallow()
api = Api() if strtobool(os.environ.get('SWAGGER_UI_ENABLED', '0')) \
    else Api(doc=False)
