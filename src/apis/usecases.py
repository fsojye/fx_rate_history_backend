import calendar
import os
from datetime import date, datetime, timedelta

import requests

from apis.custom_exceptions import (DataRequestException, InvalidDataException,
                                    UnavailableDataException)
from apis.entities import CurrencyEntity, DateCurrencyRateEntity, DateEntity
from common.constants import DateStatusEnum
from common.logger import logging


def fetch_and_store_data():
    """Main interactor method for fetching data from third party API and storing fetched data to database.

    Lookup the last date element;
    Create date object with status = PENDING;
    Send request to API for next date data;
    Validates and insert data to database;
    Update date object with status = SUCCESS or FAILED
    """

    logging.info('Starting data collection')
    try:
        next_date = _get_next_date(_get_last_date_from_db())
        logging.info(next_date)
        date_entity = _insert_date_to_db(next_date)
        data = _fetch_data_from_provider(
            f"{os.environ['DATASOURCE_HOST']}/v1/{str(next_date)}?access_key={os.environ['DATASOURCE_API_KEY']}&format=1"
        )
        logging.debug(data)
        _validate_data(data)

        _insert_data_to_db(data, date_entity)
        _update_date_status_in_db(date_entity, DateStatusEnum.SUCCESS.value)
        logging.info('Data collection success')
    except (InvalidDataException, DataRequestException):
        _update_date_status_in_db(date_entity, DateStatusEnum.FAILED.value)
        logging.info('Data collection failed')
    except UnavailableDataException:
        logging.info('Data is still unavailable; do nothing for now')

    logging.info('End of data collection')


def _get_last_date_from_db() -> date:
    query = DateEntity.query_last()
    return query.date if query else None


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


def _insert_date_to_db(next_date: date) -> DateEntity:
    _date = DateEntity(date=next_date)
    _date.insert()
    return _date


def _fetch_data_from_provider(url: str) -> dict:
    try:
        return requests.get(url).json()
    except Exception as e:
        raise DataRequestException(e)


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


def _insert_data_to_db(data: dict, date_entity: DateEntity):
    for k, v in data['rates'].items():
        currency_entity = CurrencyEntity(code=k)
        date_currency_rate_entity = DateCurrencyRateEntity(
            date=date_entity, currency=currency_entity, amount=v, epoch=data['timestamp'], base_ccy=data['base'])
        date_currency_rate_entity.insert()


def _update_date_status_in_db(date_ent: DateEntity, status: DateStatusEnum):
    date_ent.update(key='status', value=status)
