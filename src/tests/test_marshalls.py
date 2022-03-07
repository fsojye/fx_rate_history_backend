import pytest

from apis.marshalls import GetRatesQueryParameterSchema


@pytest.mark.parametrize('data,expected', [
    ({"symbols": ['PHP'], "start":"fake"}, {"symbols": ['PHP', 'USD', 'EUR'], "start":"fake", "end":"fake", "granularity":"month"})
])
def test_get_rates_query_parameter_schema_marshall_custom_post_load(data, expected):
    actual = GetRatesQueryParameterSchema().set_defaults(data)
    assert actual == expected
