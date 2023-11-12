import pytest
from unittest.mock import patch, Mock
import requests
from requests.exceptions import HTTPError
from supacrud.base import BaseRequester, SupabaseError


def test_base_requester_instantiation():
    base_url = "http://example.com"
    headers = {"Authorization": "Bearer token"}
    requester = BaseRequester(base_url, headers)

    assert requester.base_url == "http://example.com/"
    assert requester.headers == headers
    assert requester.retry_enabled == True
    assert requester.max_retries == 3
    assert requester.backoff_factor == 2.0
    assert set(requester.non_retriable_status_codes) == set(
        [401, 403, 404, 405, 406, 409, 410, 422]
    )
    assert isinstance(requester.session, requests.Session)


def test_base_requester_instantiation_with_override():
    base_url = "http://example.com"
    headers = {"Authorization": "Bearer token"}
    requester = BaseRequester(
        base_url,
        headers,
        override_non_retriable_status_codes=True,
        add_non_retriable_status_codes=[500, 502],
    )

    assert requester.base_url == "http://example.com/"
    assert requester.headers == headers
    assert requester.retry_enabled == True
    assert requester.max_retries == 3
    assert requester.backoff_factor == 2.0
    assert requester.non_retriable_status_codes == [500, 502]
    assert isinstance(requester.session, requests.Session)


def test_base_requester_instantiation_with_additional_status_codes():
    base_url = "http://example.com"
    headers = {"Authorization": "Bearer token"}
    requester = BaseRequester(
        base_url, headers, add_non_retriable_status_codes=[500, 502]
    )

    assert requester.base_url == "http://example.com/"
    assert requester.headers == headers
    assert requester.retry_enabled == True
    assert requester.max_retries == 3
    assert requester.backoff_factor == 2.0
    assert set(requester.non_retriable_status_codes) == set(
        [401, 403, 404, 405, 406, 409, 410, 422, 500, 502]
    )


def test_base_url_formatting():
    base_url_without_slash = "http://example.com"
    base_url_with_slash = "http://example.com/"
    headers = {"Authorization": "Bearer token"}

    requester = BaseRequester(base_url_without_slash, headers)
    assert requester.base_url == "http://example.com/"

    requester = BaseRequester(base_url_with_slash, headers)
    assert requester.base_url == "http://example.com/"


@patch("supacrud.base.urljoin")
def test_execute_with_retry_enabled(mock_urljoin):
    base_url = "http://example.com"
    headers = {"Authorization": "Bearer token"}
    requester = BaseRequester(base_url, headers, retry=True)
    mock_urljoin.return_value = "http://example.com/path"
    expected_result = {"key": "value", "status_code": 200}

    with patch("requests.Session.request") as mock_request:
        response = Mock(spec=requests.Response)
        response.status_code = 200
        response.json.return_value = expected_result
        mock_request.return_value = response

        result = requester.execute("GET", "path")

        assert result.json() == expected_result
        mock_urljoin.assert_called_once_with("http://example.com/", "path")
        mock_request.assert_called_once_with(
            "GET", "http://example.com/path", json=None, headers=headers
        )
        mock_request.return_value.raise_for_status.assert_called_once_with()


@patch("supacrud.base.urljoin")
def test_execute_with_retry_disabled(mock_urljoin):
    base_url = "http://example.com"
    headers = {"Authorization": "Bearer token"}
    requester = BaseRequester(base_url, headers, retry=False)
    mock_urljoin.return_value = "http://example.com/path"
    expected_result = {"key": "value", "status_code": 200}

    with patch("requests.Session.request") as mock_request:
        response = Mock(spec=requests.Response)
        response.status_code = 200
        response.json.return_value = expected_result
        mock_request.return_value = response

        result = requester.execute("GET", "path")

        assert result.json() == expected_result
        mock_urljoin.assert_called_once_with("http://example.com/", "path")
        mock_request.assert_called_once_with(
            "GET", "http://example.com/path", json=None, headers=headers
        )
        mock_request.return_value.raise_for_status.assert_called_once_with()


@patch("supacrud.base.urljoin")
def test_execute_handles_http_error(mock_urljoin):
    base_url = "http://example.com"
    headers = {"Authorization": "Bearer token"}
    requester = BaseRequester(base_url, headers)
    mock_urljoin.return_value = "http://example.com/path"

    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = HTTPError(
            response=Mock(status_code=400, reason="Bad Request")
        )

        with pytest.raises(SupabaseError) as exc_info:
            requester.execute("GET", "path")

        assert exc_info.value.status_code == 400
        assert "HTTP request failed" in str(exc_info.value)
        mock_urljoin.assert_called_once_with("http://example.com/", "path")
