import pytest
from unittest.mock import patch
from typing import Dict, List, Optional, Any, Union
from requests.exceptions import HTTPError

import tenacity
from supacrud import Supabase, SupabaseError
from supacrud.base import BaseRequester


class MockResponse:
    """Mock class for requests.Response"""

    def __init__(
        self,
        json_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        status_code: int = 200,
    ):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if not 200 <= self.status_code < 300:
            raise HTTPError(response=self)


class MockSession:
    """Mock class for requests.Session"""

    def __init__(self, response: MockResponse):
        self.response = response

    def request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        json: Optional[Dict[str, Any]] = None,
    ):
        return self.response


@pytest.fixture
def supabase():
    base_url = "https://example.com"
    service_role_key = "service_role_key"
    anon_key = "anon_key"
    return Supabase(base_url, service_role_key, anon_key)


def test_execute_success(supabase):
    response_data = {"message": "Success"}
    response = MockResponse(json_data=response_data, status_code=200)
    session = MockSession(response)
    supabase.session = session

    result = supabase.execute("GET", "/path")

    assert result == response_data


def test_execute_http_error(supabase):
    response_data = {"message": "Error"}
    response = MockResponse(json_data=response_data, status_code=400)
    session = MockSession(response)
    supabase.session = session

    with pytest.raises(SupabaseError) as excinfo:
        supabase.execute("GET", "/path")

    assert excinfo.value.status_code == 400
    assert str(excinfo.value) == "Error"


def test_create(supabase):
    response_data = {"message": "Record created"}
    response = MockResponse(json_data=response_data, status_code=201)
    session = MockSession(response)
    supabase.session = session

    result = supabase.create("/path", {"key": "value"})

    assert result == response_data


def test_read(supabase):
    response_data = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
    response = MockResponse(json_data=response_data, status_code=200)
    session = MockSession(response)
    supabase.session = session

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
