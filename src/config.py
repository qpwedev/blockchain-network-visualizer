

DEPTH = 2
TX_LIMIT = 500


class ApiConfig:
    """
    Configuration for the API.
    """

    def __init__(self, api_key: str, timeout: int, retries: int, delay: int):
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries
        self.delay = delay


EVERSPACE_CENTER_CONFIG = ApiConfig(
    api_key="b17a652df5d642a6aa6e9dae4601685a",
    timeout=10,
    retries=3,
    delay=1,
)
