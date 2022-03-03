from datetime import date
from json import load

import pytest

from app import app, db
from common.constants import DateStatusEnum
from models import Currency, Date


@pytest.fixture(scope='function')
def test_client():
    with app.test_client() as client:
        with app.app_context():
            with app.test_request_context('/'):
                db.create_all()
                yield client
                db.drop_all()


@pytest.fixture(scope='function')
def generate_date_data():
    with app.app_context():
        load_to_schema(Date, DATE_DATA)
        db.session.commit()


@pytest.fixture(scope='function')
def generate_currency_data():
    with app.app_context():
        load_to_schema(Currency, CURRENCY_DATA)
        db.session.commit()


def load_to_schema(table, data):
    for item in data:
        db.session.add(table(**item))


DATE_DATA = [
    dict(uuid="f54d7eb6-5fe7-4541-bb7d-8183e7ac06dc", date=date(2021, 12, 1), status=DateStatusEnum.SUCCESS.value),
    dict(uuid="9517e802-90db-4f9c-be10-a6a6ad2930f6", date=date(2021, 12, 31), status=DateStatusEnum.SUCCESS.value),
    dict(uuid="3ca2ff4c-5d92-41e8-98da-fc398b8d5a0c", date=date(2022, 1, 1), status=DateStatusEnum.SUCCESS.value),
    dict(uuid="be44af80-ea3d-40b1-b6fb-74a028761083", date=date(2022, 2, 1), status=DateStatusEnum.PENDING.value),
    dict(uuid="7b015c59-1697-4ebf-8da6-6847ac8444b8", date=date(2022, 1, 31), status=DateStatusEnum.SUCCESS.value)
]


CURRENCY_DATA = [
    dict(uuid="4d98d1e2-d52c-444e-afd5-82ef64f260f8", code="BTC"),
    dict(uuid="7f194de3-9abb-489e-bd98-96d57c176b9b", code="EUR"),
    dict(uuid="2a216c89-bdbc-4a37-9469-8147faebd9b1", code="JPY"),
    dict(uuid="6c7a43d4-4343-4708-9c8d-f35e0cfa06ab", code="PHP"),
    dict(uuid="6781c32e-6d4a-4aff-9724-9b7c28fc0c65", code="TWD"),
    dict(uuid="0c358150-1169-4f18-8238-50e5e249ef0d", code="USD"),
]
