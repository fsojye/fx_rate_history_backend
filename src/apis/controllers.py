from flask import request
from flask_restx import Resource

from apis.usecases import get_menu, get_order, post_order, process_order


class MenuController(Resource):
    """Controller class for menu resource."""
    def get(self):
        """Query product details from database
        
        Returns:
            list: products and its quantity.
        """

        return get_menu()

class OrderController(Resource):
    """Controller class for order resource."""

    def get(self, order_uuid: str):
        """Look up `order_uuid` in db and returns dictionary of order details.

        Args:
            order_uuid (str): order_uuid of order.
        """

        return get_order(order_uuid)

    def post(self):
        return post_order(request.json)

class OrderProcessorController:
    """Controller class for processing order from sqs.

    Args:
        sqs_event (dict): event object from AWS Lambda trigger.
    """

    def __init__(self, sqs_event: dict):
        self._sqs_event = sqs_event

    def process(self):
        """Consumes message from sqs."""

        process_order(self._sqs_event)