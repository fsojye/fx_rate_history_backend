from app_context import api
from apis.controllers import MenuController, OrderController

def add_resources():
    ns_menu = api.namespace('menu', path='/', ordered=True)
    ns_order = api.namespace('order', path='/', ordered=True)

    ns_menu.add_resource(MenuController, '/menu')
    ns_order.add_resource(OrderController, '/order')
    ns_order.add_resource(OrderController, '/order/<order_uuid>')
