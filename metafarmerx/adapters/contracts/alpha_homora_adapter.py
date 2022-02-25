import json

from protocols.homora.alpha_homora_v2 import AlphaHomoraV2

class AlphaHomoraAdapter(AlphaHomoraV2):
    """
    Alpha Homora adapter to get position data
    """
    def __init__(self, _filter=True):
       super().__init__("TraderJoeSpellV1", "USDC.e/AVAX")

    ##########################################################################    
    def get_position_data(self, pos_id):
        """
        Calls the HomoraBank contract 
        """
        return self.query_bank(pos_id)
    
    ##########################################################################    
    def get_pool_data(self, pos_id):
        """
        Calls the HomoraBank contract 
        """
        return self.query_pool(pos_id)