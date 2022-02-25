import os
import sys
import json
from matplotlib.font_manager import json_load
from pandas import Timedelta, to_datetime
from threading import Thread, Lock
from time import sleep

# sys.path.append("your directory/MetaFarmerX/metafarmerx")

from messaging.mfx_subscriber import MFXSubscriber
from strategy.auto_hedger import AutoHedger


class DeltaNeutral(MFXSubscriber):
    """
    Base class for delta neutral strategies
    """
    def __init__(self, _name="delta_neutral_two_positions"):
        super().__init__(_subdata_handlers=[self], _multiprocess=True)

        # Strategy Parameters
        self._name = _name
        self._risky_token = 'avalanche-2'
        self._pool = 'wchef-0xb41de9c1f50697cc3fd63f24ede2b40f6269cbcb-39'
        self._pos1_id = 0
        self._pos2_id = 0

        # Market Data Storage
        self._price_data = {}
        self._farming_apy = {}
        self._borrow_apy = {}
        self._position_info = {}

        # Initialize Rebalancing Module
        self._auto_hedger = AutoHedger(self)

    ##########################################################################    
    def on_market_data(self, data):        
        """
        Callback to process new data received through the SUB port
        """
        self.data_interpreter(data)

        self.data_processor()

        # debt ratio, price, APY for profitbaility, ITM & OTM delta calc/tracker
        
    ##########################################################################    
    def data_interpreter(self, data):        
        """
        Deserializes and stores incoming messages
        """
        # deserialize the new data
        new_data = json.loads(data)

        # store the new data 
        self._price_data = new_data['prices']
        self._farming_apy= new_data['farming_apy']
        self._borrow_apy = new_data['borrowing_apy']
        
        #TODO
        #self._position_info[''] = new_data['prices']

    ##########################################################################    
    def data_processor(self):        
        """
        Processes the new data and communicates with the Rebalancer Module
        """        
        self._auto_hedger.hedge_monitor()
        

def main():
    strategy = DeltaNeutral()
    strategy.poll()


if __name__ == "__main__":
    main()
