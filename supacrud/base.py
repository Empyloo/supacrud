import requests
import logging
from typing import Dict, List, Optional, Any, Union
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from urllib.parse import urljoin

ResponseType = Union[Dict[str, Any], List[Dict[str, Any]]]

logger = logging.getLogger(__name__)


class SupabaseError(Exception):
    """Custom exception for Supabase errors."""

    def __init__(
        self, message: str, status_code: Optional[int] = None, url: Optional[str] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.url = url


class BaseRequester:
    """Base class for making HTTP requests."""

    def __init__(self, base_url: str, headers: Dict[str, str]):
        """Initialize the requester with a base URL and headers.

        Args:
            base_url (str): The base URL of the Supabase API.
            headers (Dict[str, str]): The headers to use for requests.

        Raises:
            ValueError: If the base URL does not end with a forward slash.
        """
        self.base_url = base_url if base_url.endswith("/") else base_url + "/"
        self.headers = headers
        self.session = requests.Session()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=6),
        retry=retry_if_exception_type((requests.exceptions.RequestException,)),
    )
    def execute(
        self, method: str, path: str, data: Optional[Dict[str, Any]] = None
    ) -> ResponseType:
        """Perform an HTTP request and handle any exceptions.

        Args:
            method (str): The HTTP method to use.
            path (str): The path to perform the request at.
            data (Optional[Dict[str, Any]], optional): The data to send with the request. Defaults to None.

        Raises:
            SupabaseError: If the request fails.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        response = None
        full_url = urljoin(self.base_url, path)
        try:
            response = self.session.request(
                method, full_url, headers=self.headers, json=data
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            logger.error(f"Request failed: {err}")
            error_message = "Supabase request failed"
            if response is not None:
                error_message = response.json().get("message", error_message)
            raise SupabaseError(
                error_message,
                err.response.status_code if err.response else None,
                full_url,
            ) from err
        return response.json()


class Supabase(BaseRequester):
    """A Python client for interacting with a Supabase database.

    Attributes:
        base_url (str): The base URL of the Supabase API.
        service_role_key (str): The service role key for the Supabase API.
        anon_key (str): The anonymous key for the Supabase API.

    Methods:
        create: Create a record at the specified URL.
        read: Read records from the specified URL.
        update: Update records at the specified URL.
        delete: Delete records at the specified URL.
        rpc: Perform a POST request at the specified URL.

    Examples:
        >>> supabase = Supabase("https://example.com", "service_role_key", "anon_key")
        >>> supabase.create("rest/v1/users", {"name": "John Doe"})
        {"id": 1, "name": "John Doe"}
        >>> supabase.read("rest/v1/users")
        [{"id": 1, "name": "John Doe"}]
        >>> supabase.update("rest/v1/users", {"name": "Jane Doe"})
        [{"id": 1, "name": "Jane Doe"}]
        >>> supabase.delete("rest/v1/users")
        []
        >>> supabase.rpc("rpc/v1/users", {"name": "John Doe"})
        {"id": 1, "name": "John Doe"}
    """

    def __init__(self, base_url: str, service_role_key: str, anon_key: str):
        """Initialize the client with the base URL, service role key, and anon key.

        Args:
            base_url (str): The base URL of the Supabase API.
            service_role_key (str): The service role key for the Supabase API.
            anon_key (str): The anonymous key for the Supabase API.
        """
        headers = {
            "apikey": anon_key,
            "Content-Type": "application/json",
            "Prefer": "return=representation",
            "Authorization": f"Bearer {service_role_key}",
        }
        super().__init__(base_url, headers)

    def update_headers(self, headers: Dict[str, str]):
        """Update the headers used for requests.

        Args:
            headers (Dict[str, str]): The new headers to add or existing headers to update.
        """
        self.headers.update(headers)

    def create(self, url: str, data: Dict[str, Any]) -> ResponseType:
        """Create a record at the specified URL.

        Args:
            url (str): The URL to create the record at.
            data (Dict[str, Any]): The data to create the record with.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing POST operation at {url}")
        return self.execute("POST", url, data=data)

    def read(self, url: str) -> ResponseType:
        """Read records from the specified URL.

        Args:
            url (str): The URL to read records from.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing GET operation at {url}")
        return self.execute("GET", url)

    def update(self, url: str, data: Dict[str, Any]) -> ResponseType:
        """Update records at the specified URL.

        Args:
            url (str): The URL to update records at.
            data (Dict[str, Any]): The data to update the records with.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing PATCH operation at {url}")
        return self.execute("PATCH", url, data=data)

    def delete(self, url: str) -> ResponseType:
        """Delete records at the specified URL.

        Args:
            url (str): The URL to delete records at.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing DELETE operation at {url}")
        return self.execute("DELETE", url)

    def rpc(self, url: str, params: Optional[Dict[str, Any]] = None) -> ResponseType:
        """Perform a POST request at the specified URL.

        Args:
            url (str): The URL to perform the POST request at.
            params (Optional[Dict[str, Any]], optional): The parameters to send with the request. Defaults to None.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing RPC operation at {url}")
        return self.execute("POST", url, data=params)
