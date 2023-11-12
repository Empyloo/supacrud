import pytest
import json
import requests
from unittest.mock import patch, create_autospec

from supacrud import Supabase, SupabaseError


class MockResponse(requests.Response):
    def __init__(self, json_data, status_code):
        super(MockResponse, self).__init__()
        self._content = json.dumps(json_data).encode("utf-8")
        self.status_code = status_code
        self.encoding = "utf-8"


class MockSession:
    def __init__(self, response):
        self.response = response

    def request(self, method, url, **kwargs):
        return self.response


@pytest.fixture
def supabase():
    base_url = "https://example.com"
    service_role_key = "service_role_key"
    anon_key = "anon_key"
    return Supabase(base_url, service_role_key, anon_key)


def create_mock_response(json_data, status_code=200):
    mock_response = create_autospec(requests.Response, instance=True)
    mock_response.json.return_value = json_data
    mock_response.status_code = status_code
    return mock_response


def test_execute_success(supabase):
    response_data = {"message": "Success"}
    response = MockResponse(json_data=response_data, status_code=200)
    session = MockSession(response)
    supabase.session = session

    result = supabase.execute("GET", "/path")

    assert result.json() == response_data


def test_execute_http_error(supabase):
    response_data = {"message": "Error"}
    response = MockResponse(json_data=response_data, status_code=400)
    session = MockSession(response)
    supabase.session = session

    with pytest.raises(SupabaseError) as excinfo:
        supabase.execute("GET", "/path")

    assert excinfo.value.status_code == 400
    assert "HTTP request failed: " in str(excinfo.value)


def test_create(supabase):
    response_data = {"message": "Record created"}
    response = MockResponse(json_data=response_data, status_code=201)
    session = MockSession(response)
    supabase.session = session

    result = supabase.create("/path", {"key": "value"})

    assert result == response_data


def test_read(supabase):
    response_data = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
    mock_response = create_mock_response(response_data)

    with patch("requests.Session.request", return_value=mock_response):
        result = supabase.read("/path")
        assert result == response_data


def test_update(supabase):
    response_data = {"message": "Record updated"}
    response = MockResponse(json_data=response_data, status_code=200)
    session = MockSession(response)
    supabase.session = session

    result = supabase.update("/path", {"id": 1, "name": "John Doe"})

    assert result == response_data


def test_delete(supabase):
    response_data = {"message": "Record deleted"}
    response = MockResponse(json_data=response_data, status_code=200)
    session = MockSession(response)
    supabase.session = session

    result = supabase.delete("/path")

    assert result == response_data


def test_rpc(supabase):
    response_data = {"message": "RPC operation performed"}
    response = MockResponse(json_data=response_data, status_code=200)
    session = MockSession(response)
    supabase.session = session

    result = supabase.rpc("/path", {"param": "value"})

    assert result == response_data
