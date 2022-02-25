import json

from adapters.apis.coingecko_adapter import CoinGeckoAdapter
from adapters.apis.homora_adapter import HomoraAdapter
from adapters.apis.cream_adapter import CreamAdapter

#TODO: Create market data objects with a factory creational design pattern
class MarketData(object):
    """
    Encapsulates all market data adapters
    """
    def __init__(self):    
        # Instantiate HTTP API Adapters
        self._coingecko_adapter = CoinGeckoAdapter()
        self._homora_adapter = HomoraAdapter('wchef-0xb41de9c1f50697cc3fd63f24ede2b40f6269cbcb-39')
        self._cream_adapter = CreamAdapter()

        # Instantiate On-Chain Data Adapters
        self._alpha_homora_adapter = {}

    ##########################################################################    
    def get_transformed_data(self):
        """
        Get transformed data
        """
        return self._tranformed_data

    ##########################################################################    
    def fetch_data(self):
        """
        Fetch data from adapters
        """
        # call APIs
        self._coingecko_adapter.call()
        self._homora_adapter.call()
        self._cream_adapter.call()

        #TODO call contracts

        # get the json formatted responses
        self._prices = self._coingecko_adapter.get_response()
        self._farming_apy = self._homora_adapter.get_response()
        self._borrowing_apy = self._cream_adapter.get_response()

    ##########################################################################    
    def transform_data(self):
        """
        Transform data into target format
        """
        data = {}

        # deserialize data
        prices = json.loads(self._prices)
        farming_apy = json.loads(self._farming_apy)
        borrowing_apy = json.loads(self._borrowing_apy) 
 
        # aggregate data into a single dict
        data['prices'] = prices
        data['farming_apy'] = farming_apy
        data['borrowing_apy'] = borrowing_apy

        # convert to json
        self._tranformed_data = json.dumps(data)

