import json

from pycoingecko import CoinGeckoAPI
from .http_client import HTTPClient

class CoinGeckoAdapter(HTTPClient):
    """
    API adapter to get the price of selected tokens
    """
    def __init__(self, _filter=False):
        super().__init__(_filter=_filter)
        self._cg = CoinGeckoAPI()

    ##########################################################################    
    def call(self):
        """
        Call the pycoingecko API
        """
        self._response = self._cg.get_price(       
                                    ids=['avalanche-2', 'alpha-finance', 'joe'], 
                                    vs_currencies='usd')
        
        self._response_json = json.dumps(self._response)
        
        self.filter_response()