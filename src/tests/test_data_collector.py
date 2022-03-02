from datetime import date, datetime
from unittest import mock

import pytest

from apis.custom_exceptions import (InvalidDataException,
                                    UnavailableDataException)
from apis.usecases import (_fetch_data_from_provider, _get_last_date_from_db,
                           _get_next_date, _insert_data_to_db, _validate_data,
                           fetch_and_store_data)


@pytest.mark.usefixtures('generate_date_data')
def test_get_last_date_from_db_should_return_last_element_date_field():
    expected = date(2022, 2, 1)
    actual = _get_last_date_from_db()
    assert actual == expected


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


@mock.patch('apis.usecases.requests.get')
def test_fetch_data_from_provider_should_send_request_to_endpoint(mock_requests):
    _fetch_data_from_provider('http://localhost:8080')
    mock_requests.assert_called()


@pytest.mark.parametrize('data', [
    dict(success=True, timestamp=915235199, base='EUR', date="1999-01-01", rates=dict(JPY=133.151679, USD=1.171626, TWD=37.801368)),
    dict(success=True, timestamp=1646206622, base='EUR', date="2022-03-02", rates=dict(JPY=127.855595, USD=1.110605, TWD=31.150127, PHP=57.122291))
])
def test_validate_data_given_valid_data_should_pass(data):
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


# @mock.patch('apis.usecases.RateEntity.insert')
# @pytest.mark.parametrize('data', [
#     dict(success=True, timestamp=915235199, base='EUR', date="1999-01-01", rates=dict(JPY=133.151679, USD=1.171626, TWD=37.801368)),
#     dict(success=True, timestamp=1646206622, base='EUR', date="2022-03-02", rates=dict(JPY=127.855595, USD=1.110605, TWD=31.150127, PHP=57.122291))
# ])
# def test_insert_data_to_db_should_trigger_entity_insert_method(mock_insert, data):
#     _insert_data_to_db(data)
#     mock_insert.assert_called()


# @mock.patch('apis.usecases._get_next_date')
# @mock.patch('apis.usecases._fetch_data_from_provider')
# @mock.patch('apis.usecases._validate_data')
# @mock.patch('apis.usecases._insert_data_to_db')
# def test_fetch_and_store_data_should_trigger_expected_methods(mock_insert_data_to_db, mock_validate_data, mock_fetch_data_from_provider, mock_get_next_date):
#     fetch_and_store_data()
#     if mock_get_next_date.assert_called():
#         if mock_fetch_data_from_provider.assert_called():
#             if mock_validate_data.assert_called():
#                 mock_insert_data_to_db.assert_called()

# mock_get_next_date.assert_called()
# mock_fetch_data_from_provider.assert_called()
# mock_validate_data.assert_called()
# _insert_data_to_db.assert_called()

# @pytest.mark.parametrize('data', [
#     dict(success=True, timestamp=915235199, base='EUR', date="1999-01-01", rates=dict(JPY=133.151679, USD=1.171626, TWD=37.801368)),
#     dict(success=True, timestamp=1646206622, base='EUR', date="2022-03-02", rates=dict(JPY=127.855595, USD=1.110605, TWD=31.150127, PHP=57.122291))
# ])
# def test_feature_fetch_and_store_data_should_idk(data):
#     actual = fetch_store_data()

# return_value={
#     "success": True,
#     "timestamp": 915235199,
#     "historical": True,
#     "base": "EUR",
#     "date": "1999-01-01",
#     "rates": {
#         "ANG": 2.086282,
#         "AUD": 1.918776,
#         "AWG": 2.086282,
#         "BBD": 2.343251,
#         "BMD": 1.171626,
#         "BRL": 1.412372,
#         "BSD": 1.171626,
#         "CAD": 1.805443,
#         "CHF": 1.611044,
#         "CNY": 9.689343,
#         "DKK": 7.471248,
#         "EUR": 1,
#         "FKP": 0.707213,
#         "GBP": 0.706421,
#         "HKD": 9.104122,
#         "INR": 49.836962,
#         "JPY": 133.151679,
#         "KPW": 1054.463015,
#         "KRW": 1416.618059,
#         "MXN": 11.599099,
#         "MYR": 4.445915,
#         "NOK": 8.905698,
#         "NZD": 2.194333,
#         "PAB": 1.171626,
#         "SAR": 4.394498,
#         "SEK": 9.511108,
#         "SGD": 1.939455,
#         "SHP": 0.707213,
#         "THB": 42.848374,
#         "TWD": 37.801368,
#         "USD": 1.171626,
#         "ZAR": 6.901355
#     }
# })
