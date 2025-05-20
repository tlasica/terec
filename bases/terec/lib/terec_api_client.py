import os

from requests import Session

from terec.api.auth import api_key_headers


class TerecApiClient:
    """
    Represents a client for interacting with the Terec API.

    This class provides methods for sending HTTP GET and PUT requests to the Terec API.
    It serves as a communication layer between the application and the Terec service,
    handling authentication and session management. This enables easy interaction
    with the API and encapsulates the details of HTTP communication.

    Attributes:
        terec_url: The base URL of the Terec API. Defaults to either the `TEREC_URL`
            environment variable or "http://localhost:8000/".
        http_session: An instance of the HTTP session used for making requests.
        headers: A dictionary containing API key and other relevant
            authentication headers for requests.
    """

    def __init__(
        self, terec_api_url: str = None, http_session=None, api_key: str = None
    ):
        self.terec_url = terec_api_url or os.environ.get(
            "TEREC_URL", "http://localhost:8000/"
        )
        self.http_session = http_session or Session()
        api_key = api_key or os.environ.get("TEREC_API_KEY")
        self.headers = api_key_headers(api_key)

    def get(self, path: str, params: dict = None) -> dict:
        url = self.terec_ur(path)
        response = self.http_session.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def set_api_key(self, api_key: str) -> None:
        self.headers = api_key_headers(api_key)

    def terec_ur(self, path):
        url = f"{self.terec_url.rstrip('/')}/{path.lstrip('/')}"
        return url

    def put(self, path: str, body: dict) -> dict:
        url = self.terec_ur(path)
        response = self.http_session.put(url, headers=self.headers, json=body)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, body: dict) -> dict:
        url = self.terec_ur(path)
        response = self.http_session.post(url, headers=self.headers, json=body)
        response.raise_for_status()
        return response.json()
