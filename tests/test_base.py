import pytest
from unittest.mock import (
    patch,
    create_autospec,
    MagicMock,
)
import requests

from requests.exceptions import HTTPError
import urllib3
import json

from supacrud.base import BaseRequester


class MockResponse:
    """
    A mock response class for simulating requests.Response objects.
    """

    def __init__(self, status_code: int, json_data: dict = None, text: str = ""):
        """
        Initialize the mock response object.

        Args:
            status_code (int): The HTTP status code to return.
            json_data (dict, optional): The JSON data to return. Defaults to None.
            text (str, optional): The text data to return. Defaults to an empty string.
        """
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def json(self):
        """
        Simulate the json method of a requests.Response object.

        Returns:
            dict: The JSON data of the response.
        """
        return self._json_data

    @property
    def content(self):
        """
        Simulate the content property of a requests.Response object.

        Returns:
            bytes: The content of the response.
        """
        return self.text.encode()

    def raise_for_status(self):
        if self.status_code >= 400:
            http_error_msg = f"{self.status_code} Server Error"
            raise HTTPError(http_error_msg, response=self)


class MockHTTPResponse:
    def __init__(self, status: int, data: bytes = b"", headers: dict = None):
        self.response = create_autospec(urllib3.response.HTTPResponse, instance=True)
        self.response.status = status
        self.response.data = data
        self.response.length_remaining = len(data)
        self.response.headers = headers if headers else {}
        self.response.closed = False
        self.response.reason = "OK"
        self.response.version = "HTTP/1.1"
        self.response.streaming = False
        self.response.preload_content = False

    def __getattr__(self, attr):
        return getattr(self.response, attr)

    @staticmethod
    def create(status_code: int, json_data: dict):
        response = requests.Response()
        response.status_code = status_code
        response._content = json.dumps(json_data).encode()
        return response

    def raise_for_status(self):
        if self.response.status >= 400:
            http_error_msg = f"{self.response.status} Server Error"
            raise HTTPError(http_error_msg, response=self)


def test_base_requester_instantiation():
    base_url = "http://example.com"
    api_key = "test_api_key"
    token = "test_token"
    requester = BaseRequester(base_url, api_key, token)

    assert requester.base_url == "http://example.com/"
    assert isinstance(requester.session, requests.Session)


def test_base_requester_instantiation_with_additional_status_codes():
    base_url = "http://example.com"


def test_base_url_formatting():
    base_url_without_slash = "http://example.com"
    base_url_with_slash = "http://example.com/"
    headers = {"Authorization": "Bearer token"}

    requester = BaseRequester(
        base_url_without_slash,
        "test_api_key",
        "test_token",
    )
    assert requester.base_url == "http://example.com/"

    requester = BaseRequester(
        base_url_with_slash,
        "test_api_key",
        "test_token",
    )
    assert requester.base_url == "http://example.com/"


@patch.object(urllib3.HTTPConnectionPool, "_get_conn", autospec=True)
def test_retry_mechanism(mock_get_conn, mock_responses):
    """
    This test checks if the retry mechanism works as expected.
    """
    mock_conn = MagicMock()
    mock_conn.getresponse.side_effect = mock_responses
    mock_get_conn.return_value = mock_conn
    requester = BaseRequester(
        base_url="http://mockserver",
        api_key="test_api_key",
        token="test_token",
    )
    response = requester.execute("GET", "/unavailable-endpoint")
    assert mock_get_conn.call_count == 3
