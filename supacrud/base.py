# Path: supacrud/base.py
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from tenacity import retry, stop_after_attempt, wait_exponential
from urllib.parse import urljoin

ResponseType = Union[Dict[str, Any], List[Dict[str, Any]]]

logger = logging.getLogger(__name__)

class SupabaseError(Exception):
    """Custom exception for Supabase errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, url: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.url = url

class BaseRequester:
    """Base class for making HTTP requests."""

    def __init__(self, base_url: str, headers: Dict[str, str]):
        """Initialize the requester with a base URL and headers."""
        self.base_url = base_url if base_url.endswith('/') else base_url + '/'
        self.headers = headers

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=6))
    def perform_request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> ResponseType:
        """Perform an HTTP request and handle any exceptions."""
        response = None
        full_url = self.base_url.rstrip('/') + '/' + path.lstrip('/')
        try:
            response =  requests.request(method, full_url, headers=self.headers, json=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f'Request failed: {err}')
            error_message = 'Supabase request failed'
            if response is not None:
                error_message = response.json().get('message', error_message)
            raise SupabaseError(error_message, err.response.status_code, full_url) from err
        return response.json()


class Supabase(BaseRequester):
    """A Python client for interacting with a Supabase database."""

    def __init__(self, base_url: str, service_role_key: str, anon_key: str):
        """Initialize the client with the base URL, service role key, and anon key."""
        headers = {
            'apikey': anon_key,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation',
            'Authorization': f'Bearer {service_role_key}'
        }
        super().__init__(base_url, headers)

    def update_headers(self, headers: Dict[str, str]):
        """Update the headers used for requests."""
        self.headers.update(headers)

    def create(self, url: str, data: Dict[str, Any]) -> ResponseType:
        """Create a record at the specified URL."""
        logger.debug(f'Performing POST operation at {url}')
        return self.perform_request('POST', url, data=data)

    def read(self, url: str) -> ResponseType:
        """Read records from the specified URL."""
        logger.debug(f'Performing GET operation at {url}')
        return self.perform_request('GET', url)

    def update(self, url: str, data: Dict[str, Any]) -> ResponseType:
        """Update records at the specified URL."""
        logger.debug(f'Performing PATCH operation at {url}')
        return self.perform_request('PATCH', url, data=data)

    def delete(self, url: str) -> ResponseType:
        """Delete records at the specified URL."""
        logger.debug(f'Performing DELETE operation at {url}')
        return self.perform_request('DELETE', url)
    
    def rpc(self, url: str, params: Optional[Dict[str, Any]] = None) -> ResponseType:
        """Perform a POST request at the specified URL."""
        logger.debug(f'Performing RPC operation at {url}')
        return self.perform_request('POST', url, data=params)
