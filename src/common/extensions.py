import os

from flask import current_app
from pynamodb.connection import Connection, table
from pynamodb.models import Model


class PynamoDBModel(Model):
    """
    Retrieve table/model connection to database
    """

    _app_config = {}

    @classmethod
    def create_table(cls):
        binds = current_app.config.get('PYNAMODB_BINDS', [])
        if cls not in binds:
            binds.append(cls)
        current_app.config['PYNAMODB_BINDS'] = binds

        super().create_table(
            wait=True,
            read_capacity_units=1,
            write_capacity_units=1
        )

    @classmethod
    def delete_table(cls):
        current_app.config.get('PYNAMODB_BINDS').remove(cls)
        return super().delete_table()

    @classmethod
    def _get_connection(cls) -> table.TableConnection:
        meta = getattr(cls, "Meta", None)

        if not meta or cls._connection:
            return super()._get_connection()

        for key, value in cls._app_config.items():
            if not getattr(meta, key, None):
                setattr(meta, key, value)

        return super()._get_connection()


class PynamoDB:
    """
    Simplified flask extension class for pynamodb (https://flask.palletsprojects.com/en/2.0.x/extensiondev/)
    Sourced from: https://github.com/bl4ckst0ne/flask-pynamodb/blob/main/flask_pynamodb/model.py
    """

    Model = PynamoDBModel

    def init_app(self, app):
        conn = self._init_aws_connection(app)
        app.extensions["pynamodb"] = {
            "db": self,
            "connection": conn
        }

    def destroy_all(self):
        for model in current_app.config.get('PYNAMODB_BINDS', []):
            model.delete_table()

    def _init_aws_connection(self, app) -> Connection:
        conn = Connection(
            region=app.config.get('PYNAMODB_REGION'),
            host=app.config.get('PYNAMODB_HOST'),
            read_timeout_seconds=app.config.get('PYNAMODB_READ_TIMEOUT_SECONDS'),
            connect_timeout_seconds=app.config.get('PYNAMODB_CONNECT_TIMEOUT_SECONDS'),
            max_retry_attempts=app.config.get('PYNAMODB_MAX_RETRY_ATTEMPTS'),
            base_backoff_ms=app.config.get('PYNAMODB_BASE_BACKOFF_MS'),
            max_pool_connections=app.config.get('PYNAMODB_MAX_POOL_CONNECTIONS'),
            extra_headers=app.config.get('PYNAMODB_EXTRA_HEADERS')
        )
        conn.session.set_credentials(
            os.environ['AWS_ACCESS_KEY_ID'],
            os.environ['AWS_SECRET_ACCESS_KEY']
        )
        return conn

    @property
    def connection(self):
        try:
            return current_app.extensions["pynamodb"]["connection"]
        except KeyError:
            self.init_app(current_app)
            return current_app.extensions["pynamodb"]["connection"]
