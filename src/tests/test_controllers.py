from unittest import mock

import pytest

from apis.controllers import DataCollectorController, RatesController


@mock.patch('apis.controllers.fetch_and_store_data')
def test_data_collector_controller_must_call_fetch_and_store_data_usecase(mock_fetch_and_store_data):
    DataCollectorController.handle()
    mock_fetch_and_store_data.assert_called()


@mock.patch('apis.controllers.get_rates_data')
@mock.patch('apis.controllers.request')
def test_get_rates_controller_must_call_get_rates_data_usecase(mock_request, mock_get_rates_data):
    mock_request.parsed_query_params = ''
    rc = RatesController()
    rc.get.__wrapped__(rc)
    mock_get_rates_data.assert_called()
