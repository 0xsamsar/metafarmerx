'''
        __  ___     __        ______                              _  __
       /  |/  /__  / /_____ _/ ____/___ __________ ___  ___  ____| |/ /
      / /|_/ / _ \/ __/ __ `/ /_  / __ `/ ___/ __ `__ \/ _ \/ ___/   / 
     / /  / /  __/ /_/ /_/ / __/ / /_/ / /  / / / / / /  __/ /  /   |  
    /_/  /_/\___/\__/\__,_/_/    \__,_/_/  /_/ /_/ /_/\___/_/  /_/|_|  

'''

import sys
import zmq
import json

from time import sleep

# sys.path.append("your directory/MetaFarmerX/metafarmerx")

from adapters.market_data import MarketData


class MFXPublisher(object):
    """
    Publishes real-time market data to client strategies  
    """
    def __init__(self, _host='127.0.0.1', _protocol='tcp', _pub_port=42069, _multiprocess=True):   
        # ZeroMQ Host
        self._host = _host
        
        # Connection Protocol
        self._protocol = _protocol
        
        # TCP Connection URL Template
        self._url = self._protocol + "://" + self._host + ":"

        # SUB Socket Port
        self._pub_port = _pub_port

        self._multiprocess = _multiprocess
        
        if self._multiprocess == False:
            self.create_context()

        # set the frequency of data updates (s)
        self._sleep_delay = 1 

        # Instantiate Market Data Object
        self._market_data = MarketData()
        print("[INITIALIZED] MetaFarmerX Market Feeds")

        # Market Data Client Configuration
        self._PUBLISH_MARKET_DATA = True

        # Run MetaFarmerX
        self._RUN = True

    ##########################################################################
    def create_context(self):
        """
        Creates ZeroMQ Context
        """
        # ZeroMQ Context
        self._zmq_context = zmq.Context()

        # Create Sockets
        self._pub_socket = self._zmq_context.socket(zmq.PUB)
        self._pub_socket.setsockopt(zmq.SNDHWM, 1)
        self._pub_socket.setsockopt(zmq.LINGER, 0)

        # Connect PUB Socket to send market data
        self._pub_socket.bind(self._url + str(self._pub_port)) 


    ##########################################################################    
    def remote_send(self, _socket, _data):
        """
        Send string on socket
        """
        try:
            _socket.send_json(_data)
        except zmq.error.Again:
            print("\nResource timeout... trying again")
            sleep(self._sleep_delay)
      
    ##########################################################################    
    def update_data(self):
        """
        Retreive market data
        """
        self._market_data.fetch_data()
        self._market_data.transform_data()
      
    ##########################################################################
    def on_tick(self):
        """
        Publish market data on PUB socket
        """
        if self._PUBLISH_MARKET_DATA:
            # update market data
            self.update_data()

            # send data to client through PUB socket
            self.remote_send(self._pub_socket, self._market_data._tranformed_data)

    ##########################################################################
    def run(self):
        """
        Run MetaFarmerX
        """
        if self._multiprocess:
            self.create_context()

        while self._RUN:
            # blocking delay
            sleep(self._sleep_delay)

            self.on_tick()

