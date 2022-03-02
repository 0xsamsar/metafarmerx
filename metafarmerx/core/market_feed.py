import json

from adapters.apis.coingecko_adapter import CoinGeckoAdapter
from adapters.apis.cream_adapter import CreamAdapter
from adapters.apis.alpha_adapter import AlphaAdapter
from adapters.contracts.alpha_homora_adapter import AlphaHomoraAdapter
from handlers.mfx_publisher import MFXPublisher


class MarketFeed(MFXPublisher):
    """
    Encapsulates all market data adapters
    """
    def __init__(self, 
                _pos_id,
                _lp_pair,
                _frequency=1,
                _multiprocess=True):  
        super().__init__(_sleep_delay=_frequency, _multiprocess=_multiprocess)

        # Instantiate position IDs
        self._pos_id = _pos_id
        self._lp_pair = _lp_pair

        # Instantiate HTTP API Adapters
        self._coingecko_adapter = CoinGeckoAdapter()
        self._alpha_adapter = AlphaAdapter(self._lp_pair)
        self._cream_adapter = CreamAdapter()

        # Instantiate On-Chain Data Adapters
        self._alpha_homora_adapter = AlphaHomoraAdapter(self._pos_id,
                                                        self._lp_pair,
                                                        _filter=True)

    ##########################################################################    
    def get_transformed_data(self):
        """
        Get transformed data
        """
        return self.tranformed_data

    ##########################################################################    
    def fetch_data(self):
        """
        Fetch data from adapters
        """
        # call APIs
        self._coingecko_adapter.call()
        self._alpha_adapter.call()
        self._cream_adapter.call()

        # call contracts
        self._alpha_homora_adapter.call()

        # get the json formatted responses
        self._prices = self._coingecko_adapter.get_response()
        self._farming_apy = self._alpha_adapter.get_response()
        self._borrowing_apy = self._cream_adapter.get_response()
        self._position_data, self._pool_data = self._alpha_homora_adapter.get_response()

    ##########################################################################    
    def transform_data(self):
        """
        Transform data into target format
        """
        self.market_data = {}

        # deserialize data
        prices = json.loads(self._prices)
        farming_apy = json.loads(self._farming_apy)
        borrowing_apy = json.loads(self._borrowing_apy)
        position_data = json.loads(self._position_data)
        pool_data = json.loads(self._pool_data)
 
        # aggregate data into a single dict
        self.market_data['prices'] = prices
        self.market_data['farming_apy'] = farming_apy
        self.market_data['borrowing_apy'] = borrowing_apy
        self.market_data['position_data'] = position_data
        self.market_data['pool_data'] = pool_data

        # convert to json
        self.tranformed_data = json.dumps(self.market_data)

