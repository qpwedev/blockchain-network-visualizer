import os


DEPTH = 100


class ApiConfig:
    """
    Configuration for the API.
    """

    def __init__(self, api_key: str, timeout: int, retries: int, delay: int):
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries
        self.delay = delay


everspaceCenterConfig = ApiConfig(
    api_key=os.getenv('EVERSPACE_CENTER_API_KEY'),
    timeout=10,
    retries=3,
    delay=1,
)
