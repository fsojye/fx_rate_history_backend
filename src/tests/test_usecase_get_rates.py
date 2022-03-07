from unittest import mock

import pytest
import werkzeug.exceptions

from apis.custom_exceptions import UnavailableDataException
from apis.usecases.get_rates import _get_currency_from_db, get_rates_data


@pytest.mark.usefixtures('generate_date_currency_rate_data')
class TestGetRates:
    @pytest.mark.parametrize('symbols, expected', [
        (['PHP'], 1),
        (['PHP', 'USD'], 2),
        (['JPY', 'PHP'], 2),
    ])
    def test_get_currency_from_db_must_return_expected(self, symbols, expected):
        actual = _get_currency_from_db(symbols)
        assert len(actual) == expected

    def test_get_currency_from_db_when_object_not_in_db_must_raise_unavailable_data_exception(self):
        with pytest.raises(UnavailableDataException):
            _get_currency_from_db(['FAKE', 'PHP'])

    @ mock.patch('apis.usecases.get_rates._get_currency_from_db', side_effect=UnavailableDataException)
    def test_get_rates_data_given_non_existent_symbol_must_raise_404(self, mock_get_currency_from_db):
        with pytest.raises(werkzeug.exceptions.HTTPException):
            get_rates_data(dict(symbols=[]))
