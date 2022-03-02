import json
from threading import Lock, Thread
from time import sleep

from brownie import config, accounts
from controllers.protocols.alpha_homora_v2.alpha_homora_v2 import AlphaHomoraV2
from handlers.mfx_subscriber import MFXSubscriber
from pandas import Timedelta, to_datetime
from scripts.config_manager import get_account

from .auto_hedger import AutoHedger


class Strategy(MFXSubscriber):
    """
    Class for delta neutral strategies
    """
    def __init__(self,
                _pos_id, 
                _lp_pair, 
                _leverage, 
                _supply_amt, 
                _stable_borrow_amt,
                _risky_borrow_amt):
        super().__init__(_subdata_handlers=[self], _multiprocess=True)
        
        # Strategy Parameters
        self._pos_id = _pos_id
        self._lp_pair = _lp_pair
        self._leverage = _leverage
        self._supply_amt = _supply_amt
        self._stable_borrow_amt = _stable_borrow_amt
        self._risky_borrow_amt = _risky_borrow_amt

        self._risky_token = config["alpha-homora"]["pools"][self._lp_pair]["riskyTokenCGID"]

        # Market Data Storage
        self._market_data = {}

        # Initialize Blockchain Execution Layer
        self._account = get_account()
        self._protocol_controller = AlphaHomoraV2(self._pos_id, self._lp_pair, self._account)

        # Initialize Rebalancing Module
        self._auto_hedger = AutoHedger(self)

    ##########################################################################    
    def get_price(self):        
        """
        Get price of risky (non-stable) token
        """
        return self._price_data   

    ##########################################################################    
    def on_market_data(self, data):        
        """
        Callback to process new data received through the SUB port
        """
        self.data_interpreter(data)
        self.data_processor()
        
    ##########################################################################    
    def data_interpreter(self, data):        
        """
        Deserializes and stores incoming messages
        """
        # deserialize and store the new data
        self._market_data = json.loads(data)

        #TODO: Decouple borrowed tokens from impl.
        self._price_data = self._market_data['prices'][self._risky_token]["usd"] 
        self._borrow_apy = (((self._leverage/4) * (self._market_data['borrowing_apy']['iWAVAX'])) + \
                            (((4-self._leverage)/4) * (self._market_data['borrowing_apy']['iUSDC.E'])))
        self._total_apy = self._leverage * (float(self._market_data['farming_apy']['totalAPY'])/100 - self._borrow_apy)
        self._debt_ratio = self._market_data['position_data'][1] / self._market_data['position_data'][0]
   
    ##########################################################################    
    def data_processor(self):        
        """
        Processes the new data and communicates with the Rebalancer Module
        """ 
        self._auto_hedger.hedge_monitor()
        
