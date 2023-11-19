import pytest
from unittest.mock import patch, MagicMock
from urllib3.connectionpool import HTTPConnectionPool
from urllib3.response import HTTPResponse

from supacrud.retry import create_retry_session


@patch.object(HTTPConnectionPool, "_get_conn", autospec=True)
def test_create_retry_session_retries(mock_get_conn, mock_responses):
    """
    This test checks if the create_retry_session function correctly retries when it receives a 500 or 429 status code.
    """
    mock_conn = MagicMock()
    mock_conn.getresponse.side_effect = mock_responses
    mock_get_conn.return_value = mock_conn
    session = create_retry_session(api_key="test_key", token="test_token")
    response = session.get("http://mockserver/unavailable-endpoint")
    assert mock_get_conn.call_count == 3


@patch.object(HTTPConnectionPool, "_get_conn", autospec=True)
def test_create_retry_session_no_retries(mock_get_conn):
    """
    This test checks if the create_retry_session function does not retry when it receives a 200 status code.
    """
    mock_response = MagicMock(spec=HTTPResponse)
    mock_response.status = 200
    mock_response.getheader.return_value = None
    mock_response.headers = {}
    mock_response.length_remaining = 0
    mock_response.reason = "OK"

    mock_conn = MagicMock()
    mock_conn.getresponse.return_value = mock_response
    mock_get_conn.return_value = mock_conn

    session = create_retry_session(api_key="test_key", token="test_token")
    response = session.get("http://mockserver/unavailable-endpoint")
    assert mock_get_conn.call_count == 1
