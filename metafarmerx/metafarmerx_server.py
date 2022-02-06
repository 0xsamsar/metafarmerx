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

from zmq.utils.monitor import recv_monitor_message

class MetaFarmerXServer():

    """
    MetaFarmerX Server
    """
    def __init__(self, 
        _ServerID='mfx-client',    # Unique ID for this client
        _host='localhost',         # Host to connect to
        _protocol='tcp',           # Connection protocol
        _PUSH_PORT=32768,          # Port for Receiving commands
        _PULL_PORT=32769,          # Port for Sending responses
        _PUB_PORT=32770):          # Port for Publishing prices

    
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
        self._PUSH_PORT = _PUSH_PORT
        self._PULL_PORT = _PULL_PORT
        self._PUB_PORT = _PUB_PORT
        
        # Create Sockets
        self._PUSH_SOCKET = self._ZMQ_CONTEXT.socket(zmq.PUSH)
        
        self._PULL_SOCKET = self._ZMQ_CONTEXT.socket(zmq.PULL)
        
        self._PUB_SOCKET = self._ZMQ_CONTEXT.socket(zmq.PUB)
        
        # Bind PUSH Socket to receive commands from MetaFarmerXConnector
        self._PUSH_SOCKET.connect(self._URL + str(self._PUSH_PORT))
        print("[INIT] Ready to send commands to MetaFarmerX (PUSH): " + str(self._PUSH_PORT))
        
        # Connect PULL Socket to send responses to MetaFarmerXConnector
        self._PULL_SOCKET.connect(self._URL + str(self._PULL_PORT))
        print("[INIT] Listening for responses from MetaFarmerX (PULL): " + str(self._PULL_PORT))
        
        # Connect PUB Socket to send market data to MetaFarmerXConnector
        print("[INIT] Listening for market data from MetaFarmerX (SUB): " + str(self._PUB_PORT))
        self._SUB_SOCKET.connect(self._URL + str(self._PUB_PORT))
        
       
    ##########################################################################
    
  