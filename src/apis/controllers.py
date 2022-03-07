
from flask import request
from flask_accepts import accepts
from flask_restx import Resource

from apis.marshalls import get_rates_query_params_schema
from apis.usecases import fetch_and_store_data, get_rates_data
from app_context import api


class DataCollectorController:
    @classmethod
    def handle(cls):
        fetch_and_store_data()


class RatesController(Resource):
    @classmethod
    @accepts(
        query_params_schema=get_rates_query_params_schema,
        # dict(name='symbols', location='args', type=list, required=True),
        # dict(name='granularity', location='args', type=str, choices=['yearly', 'monthly']),
        # dict(name='start', location='args', type=str, required=True),
        # dict(name='end', location='args', type=str),
        api=api
    )
    def get(self):
        return get_rates_data(request.parsed_query_params)
