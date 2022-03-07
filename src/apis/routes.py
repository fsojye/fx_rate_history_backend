from apis.controllers import RatesController
from app_context import api


def add_resources():
    rate_ns = api.namespace('rates', path='/', ordered=True)

    rate_ns.add_resource(RatesController, '/rates')
