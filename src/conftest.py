import os

import pytest
from moto import mock_dynamodb2, mock_sqs

from app import app, db
from common.middlewares import aws_client
from models import ProductLookup, Order

@pytest.fixture(scope='function')
def test_client():
    with app.test_client() as client:
        with app.app_context():
            with app.test_request_context('/'):
                with mock_dynamodb2():
                    yield client
                    # clean up
                    db.destroy_all()

@pytest.fixture(scope='function')
def generate_sqs():
    with mock_sqs():
        aws = aws_client('sqs')
        response = aws.create_queue(QueueName=os.environ['ORDER_QUEUE'])
        os.environ['ORDER_QUEUE_URL'] = response['QueueUrl']

@pytest.fixture(scope='function')
def generate_menu_data():
    with mock_dynamodb2():
        # setup
        ProductLookup.create_table()

        with ProductLookup.batch_write() as batch:
            for item in FAKE_MENU:
                batch.save(ProductLookup(
                    item['name'],
                    quantity=item.get('quantity', 0)
                ))

@pytest.fixture(scope='function')
def create_order_table():
    with mock_dynamodb2():
        # setup
        Order.create_table()

@pytest.fixture(scope='function')
def generate_order_data():
    with mock_dynamodb2():
        Order.create_table()
        with Order.batch_write() as batch:
            for item in FAKE_ORDERS:
                batch.save(Order(
                    item['order_uuid'],
                    items=item['items'],
                    status=item.get('status', 'PENDING')
                ))


FAKE_MENU = [
    {"name": "Pork chop", "quantity": 10},
    {"name": "Rice", "quantity": 10},
    {"name": "Chopsuey"},
    {"name": "Water", "quantity": -1}
]

FAKE_ORDERS = [
    dict(order_uuid='abcd1234', items=[{"name": "Water", "quantity": 2}], status='PENDING'),
    dict(order_uuid='123415', items=[{"name": "xxx", "quantity": 2}], status='COMPLETED'),
    dict(order_uuid='abcd123415', items=[{"name": "YYY", "quantity": 11}], status='PENDING')
]