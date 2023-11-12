import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException
from requests.models import Response
from supacrud.retry import retry


@patch("time.sleep", return_value=None)
def test_retry(mock_sleep):

    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 500

    @retry(
        max_retries=2, backoff_factor=1, non_retriable_status_codes=[400, 401, 403, 404]
    )
    def func_that_raises():
        raise RequestException(response=mock_response)

    with pytest.raises(RequestException):
        func_that_raises()

    assert mock_sleep.call_count == 2


@patch("time.sleep", return_value=None)
def test_retry_with_non_retriable_status_code(mock_sleep):

    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 400

    @retry(
        max_retries=2, backoff_factor=1, non_retriable_status_codes=[400, 401, 403, 404]
    )
    def func_that_raises():
        raise RequestException(response=mock_response)

    with pytest.raises(RequestException):
        func_that_raises()

    assert mock_sleep.call_count == 0


@patch("time.sleep", return_value=None)
def test_retry_with_successful_request(mock_sleep):

    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200

    @retry(
        max_retries=2, backoff_factor=1, non_retriable_status_codes=[400, 401, 403, 404]
    )
    def func_that_succeeds():
        return mock_response

    response = func_that_succeeds()

    assert response.status_code == 200
    assert mock_sleep.call_count == 0
