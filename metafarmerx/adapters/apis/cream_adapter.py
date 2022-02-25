import json

from .http_client import HTTPClient


class CreamAdapter(HTTPClient):
    """
    API adapter to get the Borrow APY
    """
    def __init__(self, _filter=True):
        self._query = {'comptroller': 'avalanche'}
        self._uri = 'https://api.cream.finance/api/v1/crtoken'
        self._filter_keys = ['iWAVAX','iUSDT.E','iUSDC.E','iDAI.E']
        super().__init__(self._uri, self._query, _filter, self._filter_keys)

    ##########################################################################    
    def filter_response(self):
        """
        Filter response by accesing whitelisted keys
        """
        if self._filter:
            response = self._response.json()
            result = {'iWAVAX':0.0,'iUSDT.E':0.0,'iUSDC.E':0.0,'iDAI.E':0.0}
            
            for key in response:
                if key['symbol'] in self._filter_keys:
                    result[key['symbol']] = float(key["borrow_apy"]["value"]) 
            
            self._response_json = json.dumps(result)
