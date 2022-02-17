import os
from pandas import Timedelta, to_datetime
from threading import Thread, Lock
from time import sleep

from base_strategy import BaseStrategy

#############################################################################
###############             DELTA NEUTRAL FARMING             ###############
#############################################################################


class DeltaNeutral(BaseStrategy):
    
    def __init__(self, _name="DELTA_NEUTRAL"):
        
        # Strategy params
        self._pool = ''
        self._position1_data = ''
        self._position2_data = ''

        super().__init__(_name,_subdata_handlers = [self])
        
        # lock for acquire/release of ZeroMQ connector
        #self._lock = Lock()
        
    ##########################################################################    
    def onSubData(self, data):        
        """
        Callback to process new data received through the SUB port
        """
        print(data)
        #TODO
        #parse data and set params
        #set data format once deciding what we need
        # debt ratio, price, APY for profitbaility, ITM & OTM delta calc/tracker
        
    
    def create_positions():
        pass

    def rebalance_positions():
        pass


    ##########################################################################    
    def run(self):        
        """
        Starts Strategy
        """        

        # Subscribe to market data

        # If trigger is satisfied -> rebalance position 
        # calculate debt ratio to find health factor (--> What's the most optimial setting? 
        # Is it delta of itm and otm? Ask Sert and do something simple first
        #TODO
        #call brownie functions -> if it doesn't work then use web3
        pass


def main():
    strategy = DeltaNeutral()
    strategy._MFX_Poll_Data_()


if __name__ == "__main__":
    main()
