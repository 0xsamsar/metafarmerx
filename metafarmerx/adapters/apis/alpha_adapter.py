from brownie import Contract, config

from .http_client import HTTPClient


class AlphaAdapter(HTTPClient):
    """
    API adapter to get the Farming APY
    """
    def __init__(self, _lp_pair, _filter=True):   
        self._uri = 'https://homora-api.alphafinance.io/v2/43114/apys'
        self._filter_keys = [config["alpha-homora"]["pools"][_lp_pair]["key"]]
        super().__init__(self._uri, {}, _filter, self._filter_keys)

