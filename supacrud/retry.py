import requests
from typing import Dict, Any, Callable, List
import functools
import time

ResponseType = Dict[str, Any]


def retry(
    max_retries: int, backoff_factor: float, non_retriable_status_codes: List[int]
):
    def decorator_retry(func: Callable[..., Any]):
        @functools.wraps(func)
        def wrapper_retry(*args: Any, **kwargs: Any) -> Any:
            attempts = 0
            while attempts < max_retries:
                try:
                    response = func(*args, **kwargs)
                    if isinstance(response, requests.Response):
                        if response.status_code not in non_retriable_status_codes:
                            return response
                    else:
                        if (
                            response.get("status_code")
                            not in non_retriable_status_codes
                        ):
                            return response
                except requests.exceptions.RequestException as e:
                    if (
                        not isinstance(e.response, requests.Response)
                        or e.response.status_code in non_retriable_status_codes
                    ):
                        raise
                attempts += 1
                time.sleep(backoff_factor**attempts)
            return func(*args, **kwargs)

        return wrapper_retry

    return decorator_retry
