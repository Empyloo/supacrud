# conftest.py
import pytest
from unittest.mock import patch, MagicMock
from urllib3.response import HTTPResponse
from supacrud import Supabase


@pytest.fixture
def supabase():
    base_url = "http://example.com"
    service_role_key = "key"
    return Supabase(base_url, service_role_key)


@pytest.fixture
def mock_responses():
    """
    This fixture creates a list of mock HTTP responses.
    Each response is a MagicMock object that mimics the behavior of an HTTPResponse object.
    """
    mock_response = MagicMock(spec=HTTPResponse)
    mock_response.status = 500
    mock_response.getheader.return_value = "1"
    mock_response.headers = {"Retry-After": "1"}
    mock_response.length_remaining = 0
    mock_response.reason = "Internal Server Error"

    mock_response2 = MagicMock(spec=HTTPResponse)
    mock_response2.status = 429
    mock_response2.getheader.return_value = "1"
    mock_response2.headers = {"Retry-After": "1"}
    mock_response2.length_remaining = 0
    mock_response2.reason = "Too Many Requests"

    mock_response3 = MagicMock(spec=HTTPResponse)
    mock_response3.status = 200
    mock_response3.getheader.return_value = None
    mock_response3.headers = {}
    mock_response3.length_remaining = 0
    mock_response3.reason = "OK"

    return [mock_response, mock_response2, mock_response3]
