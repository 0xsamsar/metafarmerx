import os
from pandas import Timedelta, to_datetime
from threading import Thread, Lock
from time import sleep

#############################################################################
###############             DELTA NEUTRAL FARMING             ###############
#############################################################################

class DeltaNeutral(object):
    
    def __init__(self, _name="DELTA_NEUTRAL"):
        
        # This strategy's variables
        self._num_positions = ''
        self._pool = ''
        self._position1_data = ''
        self._position2_data = ''
        
        
    ##########################################################################    
    def onSubData(self, data):        
        """
        Callback to process new data received through the SUB port
        """
        pass
        
        
    ##########################################################################    
    def run(self):        
        """
        Starts Strategy
        """        

        # Subscribe to market data

        # If trigger is satisfied -> rebalance position
        pass

if __name__ == "__main__":
  pass