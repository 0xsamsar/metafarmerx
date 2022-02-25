from .http_client import HTTPClient


class HomoraAdapter(HTTPClient):
    """
    API adapter to get the Farming APY
    """
    def __init__(self, _pid, _filter=True):   
        self._uri = 'https://homora-api.alphafinance.io/v2/43114/apys'
        self._filter_keys = [_pid]
        super().__init__(self._uri, {}, _filter, self._filter_keys)

