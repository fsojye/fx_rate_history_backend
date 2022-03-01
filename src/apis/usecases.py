import json
import os
from typing import Dict, List
from uuid import uuid4

from flask import abort

from common.middlewares import aws_client
from custom_exceptions import InvalidOrderException, InvalidMessageException
from models import ProductLookup, Order


def get_menu() -> List:
    """Scans table for all items and available quantity.

    Returns:
        list: products and its quantity.
    """

    return _get_products_from_db()

def post_order(payload: List) -> Dict:
    """Validates order and send to queue.

    Args:
        payload (list): post request payload

    Returns:
        dict: returns order_uuid and order details

    Raises:
        werkzeug.exceptions.BadRequest: If `payload` is invalid
    """

    try:
        _validate_order(payload)
        order_message = _build_order_message(payload)
        _push_order_to_sqs(order_message)
        return order_message
    except InvalidOrderException:
        abort(400)

def process_order(sqs_event: Dict):
    """Retrieves order from queue and insert into the database.

    Args:
        sqs_event (dict): AWS Lambda event object from sqs
    """

    order = _parse_order_from_sqs_event(sqs_event)
    _validate_order(order['items'])
    _insert_order_to_db(order)

def get_order(order_uuid: str) -> Dict:
    """Query database for matching `order_uuid`

    Args:
        order_uuid (str): order_uuid of the order generated during processing.

    Returns:
        dict: order_uuid, items, and status of order

    Raises:
        werkzeug.exceptions.NotFound: If `order_uuid` does not exist in the database.
    """

    return _get_order_from_db(order_uuid)

def _get_products_from_db() -> List:
    return [product.attribute_values for product in ProductLookup.scan()]

def _validate_order(order: List) -> None:
    if not _is_valid_order(order):
        raise InvalidOrderException()

def _is_valid_order(order: List) -> bool:
    menu = get_menu()
    menu = {item['name'].lower():item['quantity'] for item in menu}
    try:
        if not order:
            return False
        for item in order:
            if item['name'].lower() not in menu.keys():
                return False
            if not isinstance(item['quantity'], int):
                return False
            if item['quantity'] < 1:
                return False
            if item['quantity'] > menu[item['name'].lower()] and menu[item['name'].lower()] != -1:
                return False
    except KeyError:
        return False
    except TypeError:
        return False
    return True

def _build_order_message(order: List) -> Dict:
    return dict(order_uuid=str(uuid4()), items=order)

def _push_order_to_sqs(order_message: Dict):
    client = aws_client('sqs')
    client.send_message(
        QueueUrl=os.environ['ORDER_QUEUE_URL'],
        MessageBody=json.dumps(order_message)
    )

def _parse_order_from_sqs_event(sqs_event: Dict) -> Dict:
    try:
        message = sqs_event['Records'][0]['body']
        if message:
            return json.loads(message)
        raise InvalidMessageException
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        raise InvalidMessageException(e)

def _insert_order_to_db(order: Dict):
    Order(order['order_uuid'], items=order['items']).save()

def _get_order_from_db(order_uuid: str) -> Dict:
    try:
        for order in Order.query(order_uuid):
            return order.attribute_values
        else:
            abort(404)
    except ValueError:
        abort(404)