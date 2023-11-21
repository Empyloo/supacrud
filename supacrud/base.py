import requests
import logging
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin

from supacrud.retry import create_retry_session
from supacrud.retry_on_status_const import RETRY_ON_STATUS

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
        self.message = message
        self.status_code = status_code
        self.url = url


class BaseRequester:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        token: str,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        retry_on_status: List[int] = RETRY_ON_STATUS,
        retry_methods: List[str] = [
            "HEAD",
            "GET",
            "OPTIONS",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ],
    ):
        """
        Initializes the BaseRequester instance.

        Args:
            base_url (str): The base URL for the API.
            headers (Dict[str, str]): Headers to include in the API request.
                To override the default headers, use the update_headers method.
            max_retries (int, optional): Maximum number of retries for the request. Defaults to 3.
            backoff_factor (float, optional): The factor to use for backoff between retries. Defaults to 2.0.
            retry_on_status (List[int], optional): List of status codes to retry on. Defaults to [429, 500, 502, 503, 504, 520, 521, 522, 523, 524, 525, 526].
            retry_methods (List[str], optional): List of HTTP methods to retry. Defaults to ["HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"].

        """
        self.base_url = base_url if base_url.endswith("/") else base_url + "/"
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        self.session = create_retry_session(
            api_key=api_key,
            token=token,
            total_retries=self.max_retries,
            retry_on_status=retry_on_status,
            retry_methods=retry_methods,
            backoff_factor=self.backoff_factor,
        )

    def execute(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        full_representation: bool = False,
    ) -> requests.Response:
        url = urljoin(self.base_url, path)
        headers = {"Prefer": "return=representation" if full_representation else ""}
        try:
            logger.debug(f"Sending {method} request to {url}")
            response = self.session.request(
                method=method, url=url, headers=headers, json=data
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.debug(f"Received status code {e.response.status_code} from {url}")
            message = e.response.text
            raise SupabaseError(
                message=message,
                status_code=e.response.status_code,
                url=url,
            )
        except requests.exceptions.ConnectionError as e:
            raise SupabaseError(message=str(e), url=url)
        except requests.exceptions.Timeout as e:
            raise SupabaseError(message=str(e), url=url)
        except requests.exceptions.RequestException as e:
            raise SupabaseError(message=str(e), url=url)
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

    def __init__(
        self,
        base_url: str,
        service_role_key: str,
        anon_key: str,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        retry_on_status: List[int] = RETRY_ON_STATUS,
        retry_methods: List[str] = [
            "HEAD",
            "GET",
            "OPTIONS",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ],
    ):
        """Initialize the client with the base URL, service role key, and anon key.

        Args:
            base_url (str): The base URL of the Supabase API.
            service_role_key (str): The service role key for the Supabase API.
            anon_key (str): The anonymous key for the Supabase API.
            max_retries (int, optional): Maximum number of retries for the request. Defaults to 3.
            backoff_factor (float, optional): The factor to use for backoff between retries. Defaults to 2.0.
            retry_on_status (List[int], optional): List of status codes to retry on. Defaults to [429, 500, 502, 503, 504, 520, 521, 522, 523, 524, 525, 526].
                You can override this or add to it by importing the RETRY_ON_STATUS constant, modifying it and passing it to the Supabase constructor.
            retry_methods (List[str], optional): List of HTTP methods to retry. Defaults to ["HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"].

        """

        super().__init__(
            base_url=base_url,
            api_key=anon_key,
            token=service_role_key,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            retry_on_status=retry_on_status,
            retry_methods=retry_methods,
        )

    def create(
        self, url: str, data: Dict[str, Any], full_representation: bool = False
    ) -> requests.Response:
        """Create a record at the specified URL, POST request.

        Args:
            url (str): The URL to create the record at.
            data (Dict[str, Any]): The data to create the record with.
            full_representation (bool, optional): Whether to return the full representation of the resource. Defaults to False.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing POST operation at {url}")
        return self.execute(
            "POST", url, data=data, full_representation=full_representation
        )

    def read(self, url: str, full_representation: bool = False) -> requests.Response:
        """Read records from the specified URL, GET request.

        Args:
            url (str): The URL to read records from.
            full_representation (bool, optional): Whether to return the full representation of the resource. Defaults to False.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing GET operation at {url}")
        return self.execute("GET", url, full_representation=full_representation)

    def update(
        self, url: str, data: Dict[str, Any], full_representation: bool = False
    ) -> requests.Response:
        """Update records at the specified URL, PATCH request.

        Args:
            url (str): The URL to update records at.
            data (Dict[str, Any]): The data to update the records with.
            full_representation (bool, optional): Whether to return the full representation of the resource. Defaults to False.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing PATCH operation at {url}")
        return self.execute(
            "PATCH", url, data=data, full_representation=full_representation
        )

    def delete(self, url: str, full_representation: bool = False) -> requests.Response:
        """Delete records at the specified URL, DELETE request.

        Args:
            url (str): The URL to delete records at.
            full_representation (bool, optional): Whether to return the full representation of the resource. Defaults to False.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing DELETE operation at {url}")
        return self.execute("DELETE", url, full_representation=full_representation)

    def rpc(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        full_representation: bool = False,
    ) -> requests.Response:
        """Perform a POST request at the specified URL.

        Args:
            url (str): The URL to perform the POST request at.
            params (Optional[Dict[str, Any]], optional): The parameters to send with the request. Defaults to None.
            full_representation (bool, optional): Whether to return the full representation of the resource. Defaults to False.

        Returns:
            ResponseType: The response from the Supabase API.
        """
        logger.debug(f"Performing RPC operation at {url}")
        return self.execute(
            "POST", url, data=params, full_representation=full_representation
        )
