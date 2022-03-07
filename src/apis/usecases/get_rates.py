from datetime import date

import sqlalchemy.exc
from flask import abort

from apis.custom_exceptions import UnavailableDataException
from apis.entities import CurrencyEntity
from app_context import db
from models import Date, DateCurrencyRate


def get_rates_data(query_params: dict) -> str:
    """Main interactor method for querying our database.

    Returns:
        dictionary of selected currencies price per month or year

    Args:
        query_params (dict): deserialized query parameter schema
            symbols (list): list of currency to query
            start (date): query from
            end (date): query until
            granularity (str): month | year

    Raises:
        werkzeug.exceptions.HTTPException: raised when one or more currency symbols does not exist in the database.
    """

    try:
        response = dict()
        for currency in _get_currency_from_db(query_params['symbols']):
            response[currency.code] = _filter_currency_rates_by_date(
                currency,
                query_params['start'],
                query_params['end'],
                query_params['granularity']
            )
        return response
    except UnavailableDataException:
        abort(404)


def _get_currency_from_db(symbols: list) -> list:
    try:
        return [CurrencyEntity(code=symbol).read() for symbol in symbols]
    except sqlalchemy.exc.NoResultFound:
        raise UnavailableDataException


def _filter_currency_rates_by_date(currency, start: date, end: date, granularity: str) -> dict:
    filters = [Date.date >= start, Date.date <= end]
    currency_rates = currency.rates.join(Date).filter(*filters)
    if granularity == 'year' and start != end:
        _year = db.func.extract('year', Date.date)
        return {
            int(rate[0]): rate[1] for rate in currency_rates.with_entities(_year, db.func.avg(DateCurrencyRate.amount)).group_by(_year).all()
        }
    else:
        return {
            str(rate.date.date): rate.amount for rate in currency_rates.all()
        }
