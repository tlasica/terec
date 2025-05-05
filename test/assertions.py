import httpx
import requests


def raise_for_status(res: requests.Response) -> None:
    """
    Helper for showing more context / information when status is 4xx or 5xx.
    We need to handle both httpx and requests for FastAPI client.
    """
    try:
        res.raise_for_status()
    except (requests.exceptions.HTTPError, httpx.HTTPError) as e:
        if res.text:
            raise requests.exceptions.HTTPError(
                f"{e}\nURL: {res.url}\nResponse Text: {res.text}"
            )
        else:
            raise requests.exceptions.HTTPError(f"{e}\nURL: {res.url}")
