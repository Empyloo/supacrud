import pytest
import requests
from supacrud.base import Supabase
from requests.exceptions import RequestException


def test_create(mocker):
    # Arrange
    url = "test_url"
    data = {"test_key": "test_value"}
    expected_result = {"result_key": "result_value"}
    mock_execute = mocker.patch.object(
        Supabase, "execute", return_value=expected_result
    )
    supabase = Supabase("base_url", "service_role_key", "anon_key")

    # Act
    result = supabase.create(url, data)

    # Assert
    mock_execute.assert_called_once_with("POST", url, data=data)
    assert result == expected_result


def test_read(mocker):
    # Arrange
    url = "test_url"
    expected_result = {"result_key": "result_value"}
    mock_execute = mocker.patch.object(
        Supabase, "execute", return_value=expected_result
    )
    supabase = Supabase("base_url", "service_role_key", "anon_key")

    # Act
    result = supabase.read(url)

    # Assert
    mock_execute.assert_called_once_with("GET", url)
    assert result == expected_result


def test_update(mocker):
    # Arrange
    url = "test_url"
    data = {"test_key": "test_value"}
    expected_result = {"result_key": "result_value"}
    mock_execute = mocker.patch.object(
        Supabase, "execute", return_value=expected_result
    )
    supabase = Supabase("base_url", "service_role_key", "anon_key")

    # Act
    result = supabase.update(url, data)

    # Assert
    mock_execute.assert_called_once_with("PATCH", url, data=data)
    assert result == expected_result


def test_delete(mocker):
    # Arrange
    url = "test_url"
    expected_result = {"result_key": "result_value"}
    mock_execute = mocker.patch.object(
        Supabase, "execute", return_value=expected_result
    )
    supabase = Supabase("base_url", "service_role_key", "anon_key")

    # Act
    result = supabase.delete(url)

    # Assert
    mock_execute.assert_called_once_with("DELETE", url)
    assert result == expected_result


def test_rpc(mocker):
    # Arrange
    url = "test_url"
    params = {"test_key": "test_value"}
    expected_result = {"result_key": "result_value"}
    mock_execute = mocker.patch.object(
        Supabase, "execute", return_value=expected_result
    )
    supabase = Supabase("base_url", "service_role_key", "anon_key")

    # Act
    result = supabase.rpc(url, params)

    # Assert
    mock_execute.assert_called_once_with("POST", url, data=params)
    assert result == expected_result
