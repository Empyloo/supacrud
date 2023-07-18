# Path: supacrud/base.py
import requests
import logging
from typing import Dict, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class SupabaseError(Exception):
    """Custom exception for Supabase errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, url: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.url = url

class Supabase:
    """A Python client for interacting with a Supabase database."""
    def __init__(self, base_url: str, service_role_key: str):
        """Initialize the client with the base URL and service role key."""
        self.base_url = base_url
        self.headers = {
            'apikey': service_role_key,
            'Content-Type': 'application/json'
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=6))
    def _perform_request(self, method: str, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform an HTTP request and handle any exceptions."""
        response = None
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            logger.error(f'Request failed: {err}')
            status_code = response.status_code if response is not None else None
            raise SupabaseError('Supabase request failed', status_code) from err

    def create(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a record in the specified table."""
        logger.debug(f'Creating record in {table} table')
        return self._perform_request('POST', f'{table}', data=data)

    def _validate_id(self, id: str):
        """Validate the provided id."""
        if not id:
            raise ValueError("An ID is required.")
        # Further validation logic for id could be added here.

    def _get_url(self, table: str, id: Optional[str] = None) -> str:
        """Create a url for a given table and optional id."""
        url = urljoin(self.base_url, table)
        if id is not None:
            self._validate_id(id)
            url += f'?id=eq.{id}'
        return url

    def read(self, table: str, id: Optional[str] = None, filters: Optional[str] = None) -> Dict[str, Any]:
        """Read records from the specified table, with optional filters."""
        if id is None and filters is None:
            raise ValueError("Either 'id' or 'filters' must be provided.")
        logger.debug(f'Reading records from {table} table')
        url = self._get_url(table, id)
        if filters is not None:
            url += f'&{filters}' if '?' in url else f'?{filters}'
        return self._perform_request('GET', url)

    def update(self, table: str, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record in the specified table."""
        logger.debug(f'Updating record in {table} table')
        url = self._get_url(table, id)
        return self._perform_request('PATCH', url, data=data)

    def delete(self, table: str, id: str) -> Dict[str, Any]:
        """Delete a record from the specified table."""
        logger.debug(f'Deleting record from {table} table')
        url = self._get_url(table, id)
        return self._perform_request('DELETE', url)