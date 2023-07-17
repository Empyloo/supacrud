# Path: tests/test_base.py
import pytest
from unittest.mock import patch
import requests
import tenacity
from supacrud import Supabase
from tenacity import RetryError

import pytest
from unittest.mock import patch
import requests

from supacrud.base import BaseRequester, SupabaseError


@patch('requests.request')
def test_perform_request_success(mock_request):
    """Test the successful execution of a request."""
    base_url = 'http://example.com'
    path = 'rest/v1/users'
    data = {'key': 'value'}
    headers = {'Content-Type': 'application/json'}
    mock_request.return_value.json.return_value = {'key': 'value'}

    request = BaseRequester(base_url, headers)
    response = request.perform_request('GET', path, data)

    mock_request.assert_called_once_with('GET', base_url + "/" + path, headers=headers, json=data)
    assert response == {'key': 'value'}


@patch('requests.request')
def test_perform_request_failure(mock_request):
    """Test the execution of a request when the request fails."""
    base_url = 'http://example.com'
    path = 'rest/v1/users'
    data = {'key': 'value'}
    headers = {'Content-Type': 'application/json'}
    mock_request.side_effect = requests.exceptions.RequestException

    request = BaseRequester(base_url, headers)
    with pytest.raises(RetryError):
        request.perform_request('GET', path, data)


@patch('requests.request')
def test_perform_request_retry(mock_request):
    """Test the retry mechanism of the perform_request function."""
    base_url = 'http://example.com'
    path = 'rest/v1/users'
    data = {'key': 'value'}
    headers = {'Content-Type': 'application/json'}
    mock_request.side_effect = [requests.exceptions.RequestException]*4

    request = BaseRequester(base_url, headers)
    with pytest.raises(RetryError):
        request.perform_request('GET', path, data)

    assert mock_request.call_count == 3

# In your test file
def test_perform_request(mocker):
    # Arrange
    method = 'GET'
    url = 'test_url'
    mock_request = mocker.patch('requests.request')
    mock_request.side_effect = requests.exceptions.HTTPError(response=mocker.Mock(status_code=400))
    supabase = Supabase('base_url', 'service_role_key', 'anon_key')

    # Act and Assert
    with pytest.raises(tenacity.RetryError) as exc_info:
        supabase.perform_request(method, url)
    
    assert exc_info.value.last_attempt.failed
