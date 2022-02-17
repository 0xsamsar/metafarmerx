'''             __  ___     __        ______                              _  __
               /  |/  /__  / /_____ _/ ____/___ __________ ___  ___  ____| |/ /
              / /|_/ / _ \/ __/ __ `/ /_  / __ `/ ___/ __ `__ \/ _ \/ ___/   / 
             / /  / /  __/ /_/ /_/ / __/ / /_/ / /  / / / / / /  __/ /  /   |  
            /_/  /_/\___/\__/\__,_/_/    \__,_/_/  /_/ /_/ /_/\___/_/  /_/|_|  
'''

import zmq
from time import sleep
from pandas import DataFrame, Timestamp
from threading import Thread

from adapters.api_adapter import CoinGeckoAdapter, HomoraAdapter, CreamAdapter


class MetaFarmerXServer():

    """
    MetaFarmerX Server
    """
    def __init__(self, 
        _host='127.0.0.1',         # Host to connect to
        _protocol='tcp',           # Connection protocol
        _PUB_PORT=32770):          # Port for Publishing market data

        ######################################################################
        
        # ZeroMQ Host
        self._host = _host
        
        # Connection Protocol
        self._protocol = _protocol

        # ZeroMQ Context
        self._ZMQ_CONTEXT = zmq.Context()
        
        # TCP Connection URL Template
        self._URL = self._protocol + "://" + self._host + ":"

        # Ports for PUSH, PULL and SUB sockets respectively
        self._PUB_PORT = _PUB_PORT

        # Set Configuration
        self._sleep_delay = 1 # set the frequency of market data updates (s)

        # Market Data Client Configuration
        self._PUBLISH_MARKET_DATA = True
        self._PUBLISH_SYMBOLS = []
        
        # Create Sockets
        self._PUB_SOCKET = self._ZMQ_CONTEXT.socket(zmq.PUB)
        self._PUB_SOCKET.setsockopt(zmq.SNDHWM, 1)
        self._PUB_SOCKET.setsockopt(zmq.LINGER, 0)

        
        # Connect PUB Socket to send market data to MetaFarmerXConnector
        self._PUB_SOCKET.bind(self._URL + str(self._PUB_PORT))
        print("[INIT] MetaFarmerX Initialized")

        # Instantiate APIs
        self.price = CoinGeckoAdapter()
        self.farming_apy = HomoraAdapter()
        self.borrowing_apy = CreamAdapter()

        # Run server
        self._RUN = True


    ##########################################################################    
    """
    Function to send data to Connector Client (PUSH)
    """
    def remote_send(self, _socket, _data):
        
        try:
            _socket.send_string(_data)
        except zmq.error.Again:
            print("\nResource timeout.. please try again.")
            sleep(self._sleep_delay)
      
    ##########################################################################
    """
    Function to send market data to subscribed client
    """
    def OnTick(self):
        if self._PUBLISH_MARKET_DATA == True:
            
            # get data
            #TODO get position debt info from subgraph
            self.price.call()
            self.farming_apy.call()
            self.borrowing_apy.call()

            msg = "{}: {};".format('Avalanche-2', self.borrowing_apy.call())

            print("Sending: ", msg)
            # send data
            self.remote_send(self._PUB_SOCKET, msg)

    ##########################################################################
    """
    Function to check Poller for new reponses (PULL) and market data (SUB)
    """
    def RunServer(self, string_delimiter=';', poll_timeout=1):
        
        while self._RUN:
            
            sleep(self._sleep_delay) # sleep() is in seconds
            self.OnTick()


def main():
    metafarmerx = MetaFarmerXServer()
    metafarmerx.RunServer()

if __name__ == "__main__":
    main()