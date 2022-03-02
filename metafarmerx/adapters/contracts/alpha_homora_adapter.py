import json

from controllers.protocols.alpha_homora_v2.alpha_homora_v2 import AlphaHomoraV2


class AlphaHomoraAdapter(AlphaHomoraV2):
    """
    Alpha Homora adapter to get all position data
    """
    def __init__(self,
                _pos_id,
                _lp_pair,
                _filter=True):
        super().__init__(_pos_id, _lp_pair, None)

        self._pos_id = _pos_id
        self._filter = _filter

        self._position_response = {}
        self._pool_response = {}

    ##########################################################################    
    def get_position_data(self):
        """
        Calls the HomoraBank contract 
        """
        pos_data = self.query_bank(self._pos_id)
        self._position_data = pos_data
    
    ##########################################################################    
    def get_pool_data(self):
        """
        Calls the HomoraBank contract 
        """
        pos_data = self.query_pool(self._pos_id)
        self._pool_data = pos_data

    ##########################################################################    
    def get_response(self):
        """
        Get response 
        """
        return self._position_response, self._pool_response

    ##########################################################################    
    def filter_response(self):
        """
        Filter response by accesing key pairs in the json object
        """
        if self._filter:
            self._position_response = json.dumps(self._position_data)
            self._pool_response = json.dumps(self._pool_data)

    ##########################################################################    
    def call(self):
        """
        Copntract Calls 
        """  
        self.get_position_data()
        self.get_pool_data()
        self.filter_response()
