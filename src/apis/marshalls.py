from marshmallow import post_load, validate
from sqlalchemy import true

from app_context import ma


class GetRatesQueryParameterSchema(ma.Schema):
    symbols = ma.List(ma.String(), required=true)
    granularity = ma.String(validate=validate.OneOf(['year', 'month']))
    start = ma.Date(required=true)
    end = ma.Date()

    @post_load
    def set_defaults(self, data, **kwargs):
        data['symbols'] = [symbol for symbol in list(set(data['symbols'][0].split(','))) if symbol not in ['USD', 'EUR']] + ['USD', 'EUR']
        data['granularity'] = data['granularity'] if data.get('granularity') else 'month'
        data['end'] = data['end'] if data.get('end') else data['start']
        return data


get_rates_query_params_schema = GetRatesQueryParameterSchema()
