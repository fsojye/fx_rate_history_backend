from datetime import date
from unittest import mock

import pytest

from apis.custom_exceptions import (DataRequestException, InvalidDataException,
                                    UnavailableDataException)
from apis.usecases import (_fetch_data_from_provider, _get_last_date_from_db,
                           _get_next_date, _insert_data_to_db,
                           _insert_date_to_db, _update_date_status_in_db,
                           _validate_data, fetch_and_store_data)
from common.constants import DateStatusEnum
from models import Currency, Date, DateCurrencyRate


@pytest.mark.usefixtures('generate_date_data')
def test_get_last_date_from_db_should_return_last_element_date_field():
    expected = date(2022, 2, 1)
    actual = _get_last_date_from_db()
    assert actual == expected


def test_get_last_date_from_db_given_table_empty_should_return_none():
    actual = _get_last_date_from_db()
    assert actual == None


@pytest.mark.parametrize('date, expected', [
    # seed date should start with 1999-01-01
    (None, date(1999, 1, 1)),
    # get first and last date of the month
    (date(2019, 12, 1), date(2019, 12, 31)),
    (date(2019, 12, 31), date(2020, 1, 1)),
    (date(2020, 1, 1), date(2020, 1, 31)),
    (date(2020, 1, 31), date(2020, 2, 1)),
    (date(2020, 2, 1), date(2020, 2, 29)),
    (date(2021, 2, 1), date(2021, 2, 28)),
    (date(2020, 2, 28), date(2020, 2, 29))
])
def test_get_next_data_given_valid_data_should_return_expected(date, expected):
    actual = _get_next_date(date)
    assert actual == expected


@pytest.mark.parametrize('date_parameter', [
    # next date is same with current date
    date(1999, 1, 1),
    # next date is beyond current date
    date(2000, 1, 1), date(2000, 2, 1), date(3000, 1, 1)
])
@pytest.mark.freeze_time('1999-01-31')
def test_get_next_data_given_date_in_future_should_raise_expected_exception(date_parameter):
    with pytest.raises(UnavailableDataException):
        _get_next_date(date_parameter)


@pytest.mark.parametrize('next_date', [
    date(2021, 1, 1), date(2021, 1, 2), date(2021, 1, 2)
])
def test_insert_date_to_db_should_create_object_and_generate_uuid(next_date):
    actual = _insert_date_to_db(next_date)
    assert actual.loaded_object.uuid is not None
    assert actual.loaded_object.status == DateStatusEnum.PENDING.value


@mock.patch('apis.usecases.requests.get')
def test_fetch_data_from_provider_should_send_request_to_endpoint(mock_requests):
    _fetch_data_from_provider('http://localhost:8080')
    mock_requests.assert_called()


@mock.patch('apis.usecases.requests.get', side_effect=ValueError)
def test_fetch_data_from_provider_given_exception_encountered_should_raise_data_request_exception(mock_requests):
    with pytest.raises(DataRequestException):
        _fetch_data_from_provider('http://localhost:8080')


@pytest.mark.parametrize('data', [
    dict(success=True, timestamp=915235199, base='EUR', date="1999-01-01", rates=dict(JPY=133.151679, USD=1.171626, TWD=37.801368)),
    dict(success=True, timestamp=1646206622, base='EUR', date="2022-03-02", rates=dict(JPY=127.855595, USD=1.110605, TWD=31.150127, PHP=57.122291))
])
def test_validate_data_given_valid_data_should_return_none(data):
    actual = _validate_data(data)
    assert actual is None


@pytest.mark.parametrize('data', [
    None, 'string', 10, [None, 'string', 10], {},
    # success value is False
    dict(success=False, timestamp=915235199, date="1999-01-01", base='EUR'),
    # base ccy not in data
    dict(success=True, timestamp=915235199, date="1999-01-01"),
    # timestamp does not match the date
    dict(success=True, timestamp=925235199, date="1999-01-01", base='EUR'),
])
def test_validate_data_given_invalid_data_should_raise_expected_exception(data):
    with pytest.raises(InvalidDataException):
        _validate_data(data)


@mock.patch('apis.usecases.DateEntity')
def test_update_date_status_in_db_should_trigger_data_entity_update_method(mock_date_entity):
    _update_date_status_in_db(mock_date_entity, 0)
    mock_date_entity.update.assert_called()


@mock.patch('apis.usecases.DateEntity')
@mock.patch('apis.usecases.CurrencyEntity')
@mock.patch('apis.usecases.DateCurrencyRateEntity.insert')
def test_insert_data_in_db_should_trigger_rate_entity_insert_method_multiple_times(
    mock_date_currency_rate_entity, mock_currency_entity, mock_date_entity
):
    _insert_data_to_db(data=TEST_DATA, date_entity=mock_date_entity)
    expected = len(TEST_DATA['rates'])
    actual = len(mock_date_currency_rate_entity.mock_calls)
    assert expected == actual


@mock.patch('apis.usecases._get_last_date_from_db')
@mock.patch('apis.usecases._get_next_date')
@mock.patch('apis.usecases._insert_date_to_db')
@mock.patch('apis.usecases._fetch_data_from_provider')
@mock.patch('apis.usecases._validate_data')
@mock.patch('apis.usecases._insert_data_to_db')
@mock.patch('apis.usecases._update_date_status_in_db')
def test_fetch_and_store_data_given_no_encountered_exception_should_trigger_expected_methods(
    mock_update_date_status_in_db, mock_insert_data_to_db, mock_validate_data, mock_fetch_data_from_provider, mock_insert_date_to_db, mock_get_next_date, mock_get_last_date_from_db
):
    fetch_and_store_data()
    if mock_get_last_date_from_db.assert_called():
        if mock_get_next_date.assert_called():
            if mock_insert_date_to_db.assert_called():
                if mock_fetch_data_from_provider.assert_called():
                    if mock_validate_data.assert_called():
                        if mock_insert_data_to_db.assert_called():
                            mock_update_date_status_in_db.assert_called()


@mock.patch('apis.usecases._get_last_date_from_db')
@mock.patch('apis.usecases._get_next_date', side_effect=UnavailableDataException)
@mock.patch('apis.usecases._insert_date_to_db')
@mock.patch('apis.usecases._fetch_data_from_provider')
@mock.patch('apis.usecases._validate_data')
@mock.patch('apis.usecases._insert_data_to_db')
@mock.patch('apis.usecases._update_date_status_in_db')
def test_fetch_and_store_data_given_get_next_date_raised_unavailable_data_exception_should_return_none(
    mock_update_date_status_in_db, mock_insert_data_to_db, mock_validate_data, mock_fetch_data_from_provider, mock_insert_date_to_db, mock_get_next_date, mock_get_last_date_from_db
):
    assert fetch_and_store_data() is None


@mock.patch('apis.usecases._get_last_date_from_db')
@mock.patch('apis.usecases._get_next_date')
@mock.patch('apis.usecases._insert_date_to_db')
@mock.patch('apis.usecases._fetch_data_from_provider', side_effect=DataRequestException)
@mock.patch('apis.usecases._validate_data')
@mock.patch('apis.usecases._insert_data_to_db')
@mock.patch('apis.usecases._update_date_status_in_db')
def test_fetch_and_store_data_given_fetch_data_from_provider_raised_data_request_exception_should_trigger_update_date_and_return_none(
    mock_update_date_status_in_db, mock_insert_data_to_db, mock_validate_data, mock_fetch_data_from_provider, mock_insert_date_to_db, mock_get_next_date, mock_get_last_date_from_db
):
    actual = fetch_and_store_data()
    mock_update_date_status_in_db.assert_called()
    assert actual is None


@mock.patch('apis.usecases._get_last_date_from_db')
@mock.patch('apis.usecases._get_next_date')
@mock.patch('apis.usecases._insert_date_to_db')
@mock.patch('apis.usecases._fetch_data_from_provider')
@mock.patch('apis.usecases._validate_data', side_effect=InvalidDataException)
@mock.patch('apis.usecases._insert_data_to_db')
@mock.patch('apis.usecases._update_date_status_in_db')
def test_fetch_and_store_data_given_validate_data_raised_invalid_data_exception_should_trigger_update_date_and_return_none(
    mock_update_date_status_in_db, mock_insert_data_to_db, mock_validate_data, mock_fetch_data_from_provider, mock_insert_date_to_db, mock_get_next_date, mock_get_last_date_from_db
):
    actual = fetch_and_store_data()
    mock_update_date_status_in_db.assert_called()
    assert actual is None


TEST_DATA = {
    "success": True,
    "timestamp": 1646220302,
    "historical": True,
    "base": "EUR",
    "date": "2022-03-02",
    "rates": {
        "AUD": 1.527742,
        "BTC": 2.520886e-5,
        "EUR": 1,
        "JPY": 127.916538,
        "PHP": 57.229981,
        "TWD": 31.113244,
        "USD": 1.109915,
    }
}


@pytest.mark.usefixtures('generate_currency_data')
@mock.patch('apis.usecases._get_last_date_from_db')
@mock.patch('apis.usecases._get_next_date', return_value=date(2022, 3, 2))
@mock.patch('apis.usecases._fetch_data_from_provider', return_value=TEST_DATA)
def test_fetch_and_store_data_functional(mock_fetch_data_from_provider, mock_get_next_date, mock_get_last_date_from_db):
    before = Date.query.count(), Currency.query.count(), DateCurrencyRate.query.count()
    fetch_and_store_data()
    after = Date.query.count(), Currency.query.count(), DateCurrencyRate.query.count()
    assert before == (0, 6, 0)
    assert after == (1, 7, 7)
    assert DateStatusEnum(Date.query.one().status).name == "SUCCESS"


@mock.patch('apis.usecases._get_last_date_from_db')
@mock.patch('apis.usecases._get_next_date', return_value=date(2022, 3, 2))
@mock.patch('apis.usecases._fetch_data_from_provider', side_effect=DataRequestException)
def test_fetch_and_store_data_functional_should_add_date_then_set_to_failed(mock_fetch_data_from_provider, mock_get_next_date, mock_get_last_date_from_db):
    before = Date.query.count(), Currency.query.count(), DateCurrencyRate.query.count()
    fetch_and_store_data()
    after = Date.query.count(), Currency.query.count(), DateCurrencyRate.query.count()
    assert before == (0, 0, 0)
    assert after == (1, 0, 0)
    assert DateStatusEnum(Date.query.one().status).name == "FAILED"
