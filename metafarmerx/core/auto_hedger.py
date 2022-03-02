from threading import Lock, Thread
from time import sleep

from pandas import Timedelta, to_datetime


class AutoHedger(object):
    """
    Implements the delta-neutral hedge rebalancing logic
    """
    def __init__(self, _strategy):
        # Strategy Parameters
        self._strategy = _strategy
        self._threshold = 0.04

        # Initial Parameters
        self._prev_token_price = None

        # Store history of all rebalncing actions
        self._rebalancing_history = {} 

    ##########################################################################    
    def set_threshold(self, new_threshold):
        """
        Set new threshold 
        """        
        self._threshold = new_threshold

    ##########################################################################    
    def hedge_monitor(self):        
        """
        Checks the health of the system
        """
        cur_token_price = self._strategy.get_price()

        # initialize price 
        if self._prev_token_price == None:
            self._prev_token_price = cur_token_price

        healthy = self.healthy(self._prev_token_price, 
                                        cur_token_price, 
                                        self._threshold)
        
        if healthy == False:
            self.auto_hedge()

    ##########################################################################    
    def auto_hedge(self):
        """
        Initiates rebalancing 
        """

        #TODO: Finish Impl. by Thur. meeting
        pass

    ##########################################################################    
    @staticmethod
    def healthy(prev_token_price, cur_token_price, threshold):
        """
        Determines if rebalancing is needed 
        """
        if abs(cur_token_price-prev_token_price)/prev_token_price >= threshold:
            return False

        return True
