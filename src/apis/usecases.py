import calendar
import os
from datetime import date, datetime, timedelta

import requests

from apis.custom_exceptions import (InvalidDataException,
                                    UnavailableDataException)
from apis.entities import CurrencyEntity, DateEntity, RateEntity
from common.logger import logging


def fetch_and_store_data():
    """Main interactor method for fetching data from third party API and storing fetched data to database.

    Lookup the last date element;
    Send request to API for next date data;
    Validates and insert data to database;
    """

    logging.info('Starting data collection')
    next_date = _get_next_date(_get_last_date_from_db())
    logging.debug(next_date)
    next_date = '2022-03-02'
    data = _fetch_data_from_provider(
        f"{os.environ['DATASOURCE_HOST']}/v1/{str(next_date)}?access_key={os.environ['DATASOURCE_API_KEY']}&format=1"
    )
    logging.debug(data)
    _validate_data(data)
    _insert_data_to_db(data)
    logging.info('End of data collection')


def _get_last_date_from_db() -> date:
    return DateEntity.query_last().date


def _get_next_date(current_date: date) -> date:
    # seed date is 1999-01-01
    if current_date is None:
        return date(1999, 1, 1)

    now = datetime.utcnow()
    last_day_of_current_dt_month = calendar.monthrange(current_date.year, current_date.month)[1]
    if current_date.day < last_day_of_current_dt_month:
        next_date = date(current_date.year, current_date.month, last_day_of_current_dt_month)
    elif current_date.day == last_day_of_current_dt_month:
        next_date = current_date + timedelta(days=1)
    if next_date >= date(now.year, now.month, now.day):
        raise UnavailableDataException
    return next_date


def _fetch_data_from_provider(url: str) -> dict:
    return requests.get(url).json()


def _validate_data(data: dict) -> None:
    try:
        ts_dt = datetime.utcfromtimestamp(data['timestamp'])
        if False in [
            data['success'],
            'base' in data,
            str(ts_dt.date()) == data['date']
        ]:
            raise InvalidDataException
    except (TypeError, KeyError) as e:
        raise InvalidDataException(e)


def _insert_data_to_db(data: dict) -> list:
    _date = DateEntity(date=data['date'])
    for k, v in data['rates'].items():
        ccy = CurrencyEntity(code=k)
        rate = RateEntity(date=_date, currency=ccy, amount=v, epoch=data['timestamp'], base_ccy=data['base'])
        rate.insert()
