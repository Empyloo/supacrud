import requests
import logging
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin

from supacrud.retry import retry

ResponseType = Union[Dict[str, Any], List[Dict[str, Any]]]

logger = logging.getLogger(__name__)


class SupabaseError(Exception):
    """Custom exception for Supabase errors."""

    def __init__(
        self, message: str, status_code: Optional[int] = None, url: Optional[str] = None
    ):
        """
        Initializes the SupabaseError instance.
    
        Args:
            message (str): The message to be associated with the instance.
            status_code (Optional[int], optional): The status code to be associated with the instance. Defaults to None.
            url (Optional[str], optional): The URL to be associated with the instance. Defaults to None.
        """
        super().__init__(message)
        self.status_code = status_code
        self.url = url


class BaseRequester:
    def __init__(
        self,
        base_url: str,
        headers: Dict[str, str],
        retry: bool = True,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        override_non_retriable_status_codes: bool = False,
        add_non_retriable_status_codes: Optional[List[int]] = None,
        default_non_retriable_status_codes: List[int] = [401, 403, 404, 405, 406, 409, 410, 422],
    ):
        """
        Initializes the BaseRequester instance.

        Args:
            base_url (str): The base URL for the API.
            headers (Dict[str, str]): Headers to include in the API request.
            retry (bool, optional): Whether to retry the request if it fails. Defaults to True.
            max_retries (int, optional): Maximum number of retries for the request. Defaults to 3.
            backoff_factor (float, optional): The factor to use for backoff between retries. Defaults to 2.0.
            override_non_retriable_status_codes (bool, optional): Whether to override the default non-retriable status codes. Defaults to False.
            add_non_retriable_status_codes (Optional[List[int]], optional): Additional status codes to consider as non-retriable. Defaults to None.
            default_non_retriable_status_codes (List[int], optional): Default status codes to consider as non-retriable. Defaults to [401, 403, 404, 405, 406, 409, 410, 422].
        """
        self.base_url = base_url if base_url.endswith("/") else base_url + "/"
        self.headers = headers
        self.retry_enabled = retry
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        if override_non_retriable_status_codes:
            self.non_retriable_status_codes = add_non_retriable_status_codes or []
        else:
            self.non_retriable_status_codes = list(set(default_non_retriable_status_codes + (add_non_retriable_status_codes or [])))

        self.session = requests.Session()

    def execute(
            self, method: str, path: str, data: Optional[Dict[str, Any]] = None
        ) -> requests.Response:
            """
            Executes an HTTP request with the given method, path, and data.

            Args:
                method (str): The HTTP method to use for the request.
                path (str): The path to send the request to.
                data (Optional[Dict[str, Any]], optional): The data to send with the request. Defaults to None.

            Returns:
                requests.Response: The response from the HTTP request.
            """
            url = urljoin(self.base_url, path)

            if self.retry_enabled:
                @retry(self.max_retries, self.backoff_factor, self.non_retriable_status_codes)
                def request_with_retry() -> requests.Response:
                    response = self.session.request(method, url, json=data, headers=self.headers)
                    response.raise_for_status()
                    return response

                try:
                    return request_with_retry()
                except requests.exceptions.HTTPError as e:
                    raise SupabaseError(
                        f"HTTP request failed: {e}", status_code=e.response.status_code, url=url
                    )
            else:
                response = self.session.request(method, url, json=data, headers=self.headers)
                response.raise_for_status()
                return response


class Supabase(BaseRequester):
    """A Python client for interacting with a Supabase database.

    Attributes:
        base_url (str): The base URL of the Supabase API.
        service_role_key (str): The service role key for the Supabase API.
        anon_key (str): The anonymous key for the Supabase API.

    Methods:
        create: Create a record at the specified URL, POST request.
        read: Read records from the specified URL, GET request.
        update: Update records at the specified URL, PATCH request.
        delete: Delete records at the specified URL, DELETE request.
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
        """Update the headers used for requests, UPDATE request.

        Args:
            headers (Dict[str, str]): The new headers to add or existing headers to update.
        """
        self.headers.update(headers)

    def create(self, url: str, data: Dict[str, Any]) -> ResponseType:
        """Create a record at the specified URL, POST request.

        Args:
            url (str): The URL to create the record at.
            data (Dict[str, Any]): The data to create the record with.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing POST operation at {url}")
        return self.execute("POST", url, data=data).json()

    def read(self, url: str) -> ResponseType:
        """Read records from the specified URL, GET request.

        Args:
            url (str): The URL to read records from.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing GET operation at {url}")
        return self.execute("GET", url).json()

    def update(self, url: str, data: Dict[str, Any]) -> ResponseType:
        """Update records at the specified URL, PATCH request.

        Args:
            url (str): The URL to update records at.
            data (Dict[str, Any]): The data to update the records with.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing PATCH operation at {url}")
        return self.execute("PATCH", url, data=data).json()

    def delete(self, url: str) -> ResponseType:
        """Delete records at the specified URL, DELETE request.

        Args:
            url (str): The URL to delete records at.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing DELETE operation at {url}")
        return self.execute("DELETE", url).json()

    def rpc(self, url: str, params: Optional[Dict[str, Any]] = None) -> ResponseType:
        """Perform a POST request at the specified URL.

        Args:
            url (str): The URL to perform the POST request at.
            params (Optional[Dict[str, Any]], optional): The parameters to send with the request. Defaults to None.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing RPC operation at {url}")
        return self.execute("POST", url, data=params).json()
