# Path: tests/test_base.py
import pytest
from unittest.mock import patch
import requests
from supacrud import Supabase
from tenacity import RetryError

def setup():
    base_url = 'http://example.com'
    service_role_key = 'key'
    supabase = Supabase(base_url, service_role_key)
    return supabase

@patch('requests.request')
def test_perform_request_success(mock_request):
    supabase = setup()
    mock_request.return_value.json.return_value = {'key': 'value'}
    response = supabase._perform_request('GET', 'http://example.com')
    mock_request.assert_called_once()
    assert response == {'key': 'value'}

@patch('requests.request')
def test_perform_request_exception(mock_request):
    supabase = setup()
    mock_request.side_effect = requests.exceptions.RequestException
    with pytest.raises(RetryError):
        supabase._perform_request('GET', 'http://example.com')
    assert mock_request.call_count == 3

@patch.object(Supabase, '_perform_request')
def test_create(mock_perform_request):
    """Test the creation of a record."""
    supabase = setup()
    mock_perform_request.return_value = {'key': 'value'}
    response = supabase.create('table', {'key': 'value'})
    mock_perform_request.assert_called_once_with('POST', 'table', data={'key': 'value'})
    assert response == {'key': 'value'}

@patch.object(Supabase, '_perform_request')
def test_read_with_id(mock_perform_request):
    """Test reading a record with an ID."""
    supabase = Supabase('http://example.com', 'service_role_key')
    mock_perform_request.return_value = {'key': 'value'}
    supabase.read('table', id='123')
    mock_perform_request.assert_called_once_with('GET', 'http://example.com/table?id=eq.123')

@patch.object(Supabase, '_perform_request')
def test_read_with_filters(mock_perform_request):
    """Test reading records with filters."""
    supabase = Supabase('http://example.com', 'service_role_key')
    mock_perform_request.return_value = {'key': 'value'}
    supabase.read('table', filters='age=gte.18&student=is.true')
    mock_perform_request.assert_called_once_with('GET', 'http://example.com/table?age=gte.18&student=is.true')

@patch.object(Supabase, '_perform_request')
def test_update(mock_perform_request):
    """Test updating a record with an ID."""
    supabase = Supabase('http://example.com', 'service_role_key')
    mock_perform_request.return_value = {'key': 'value'}
    supabase.update('table', id='123', data={'key': 'new_value'})
    mock_perform_request.assert_called_once_with('PATCH', 'http://example.com/table?id=eq.123', data={'key': 'new_value'})

@patch.object(Supabase, '_perform_request')
def test_delete(mock_perform_request):
    """Test deleting a record with an ID."""
    supabase = Supabase('http://example.com', 'service_role_key')
    mock_perform_request.return_value = {'key': 'value'}
    supabase.delete('table', id='123')
    mock_perform_request.assert_called_once_with('DELETE', 'http://example.com/table?id=eq.123')
