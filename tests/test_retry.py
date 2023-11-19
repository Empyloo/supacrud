import pytest
from unittest.mock import patch
from unittest.mock import patch, MagicMock
from urllib3.connectionpool import HTTPConnectionPool
from urllib3.response import HTTPResponse
from supacrud.retry import create_retry_session


class TestCreateRetrySession:
    def test_default_retry_settings(self):
        session = create_retry_session(api_key="test_key", token="test_token")
        assert session.headers["apikey"] == "test_key"
        assert session.headers["Authorization"] == "Bearer test_token"
        adapter = session.adapters["http://"]
        assert adapter.max_retries.total == 3
        assert adapter.max_retries.status_forcelist == [
            429,
            500,
            502,
            503,
            504,
            520,
            521,
            522,
            523,
            524,
            525,
            526,
        ]
        assert adapter.max_retries.allowed_methods == [
            "HEAD",
            "GET",
            "OPTIONS",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ]
        assert adapter.max_retries.backoff_factor == 1

    def test_custom_retry_settings(self):
        session = create_retry_session(
            api_key="test_key",
            token="test_token",
            total_retries=5,
            retry_on_status=[400, 401, 403],
            retry_methods=["GET", "POST"],
            backoff_factor=2,
        )
        assert session.headers["apikey"] == "test_key"
        assert session.headers["Authorization"] == "Bearer test_token"
        adapter = session.adapters["http://"]
        assert adapter.max_retries.total == 5
        assert adapter.max_retries.status_forcelist == [400, 401, 403]
        assert adapter.max_retries.allowed_methods == ["GET", "POST"]
        assert adapter.max_retries.backoff_factor == 2

    def test_session_headers(self):
        session = create_retry_session(api_key="test_key", token="test_token")
        assert session.headers["apikey"] == "test_key"
        assert session.headers["Authorization"] == "Bearer test_token"

    def test_api_key_type_error(self):
        with pytest.raises(TypeError):
            create_retry_session(api_key=123, token="test_token")

    def test_token_type_error(self):
        with pytest.raises(TypeError):
            create_retry_session(api_key="test_key", token=123)

    def test_total_retries_type_error(self):
        with pytest.raises(TypeError):
            create_retry_session(
                api_key="test_key", token="test_token", total_retries="3"
            )


def test_create_retry_session_retries():
    with patch.object(HTTPConnectionPool, "_get_conn", autospec=True) as mock_get_conn:

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
        mock_conn = MagicMock()
        mock_conn.getresponse.side_effect = [
            mock_response,
            mock_response2,
            mock_response3,
        ]
        mock_get_conn.return_value = mock_conn
        session = create_retry_session(api_key="test_key", token="test_token")
        response = session.get("http://mockserver/unavailable-endpoint")
        assert mock_get_conn.call_count == 3
