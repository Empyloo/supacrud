import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List

from supacrud.retry_on_status_const import RETRY_ON_STATUS

logger = logging.getLogger(__name__)


def create_retry_session(
    api_key: str,
    token: str,
    total_retries: int = 3,
    retry_on_status: List[int] = None,
    retry_methods: List[str] = None,
    backoff_factor: (int, float) = 1,
) -> requests.Session:
    """
    Create a requests session with a retry strategy.

    Args:
        api_key (str): The API key to be used for authentication.
        token (str): The token to be used for authentication.
        total_retries (int): Total number of retries. 0 means no retries.
        retry_on_status (List[int]): List of status codes to retry on.
        retry_methods (List[str]): List of HTTP methods to retry.
        backoff_factor (int, float): Backoff factor for retries.

    Returns:
        requests.Session: A requests session with a configured retry strategy.
    """
    if retry_on_status is None:
        retry_on_status = RETRY_ON_STATUS
    if retry_methods is None:
        retry_methods = [
            "HEAD",
            "GET",
            "OPTIONS",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ]

    if not isinstance(api_key, str):
        raise TypeError("api_key must be a string")
    if not isinstance(token, str):
        raise TypeError("token must be a string")
    if not isinstance(total_retries, int):
        raise TypeError("total_retries must be an integer")
    if not isinstance(retry_on_status, list) or not all(
        isinstance(status, int) for status in retry_on_status
    ):
        raise TypeError("retry_on_status must be a list of integers")
    if not isinstance(retry_methods, list) or not all(
        isinstance(method, str) for method in retry_methods
    ):
        raise TypeError("retry_methods must be a list of strings")
    if not isinstance(backoff_factor, (int, float)):
        raise TypeError("backoff_factor must be an integer or float")

    try:
        retry_strategy = Retry(
            total=total_retries,
            status_forcelist=retry_on_status,
            allowed_methods=retry_methods,
            backoff_factor=backoff_factor,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers["apikey"] = api_key
        session.headers["Authorization"] = f"Bearer {token}"
    except Exception as e:
        logger.error("Error creating retry session", exc_info=True)
        raise e
    return session
