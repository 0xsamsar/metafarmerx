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

        # Set Configuration
        self._MILLISECOND_TIMER = 1
        self._MILLISECOND_TIMER_PRICES = 500
        self._MAIN_STRING_DELIMITER = ":|:"
        self._sleep_delay = 1

        # Market Data Client Configuration
        self._PUBLISH_MARKET_DATA = True
        self._PUBLISH_SYMBOLS = []
        
        # Create Sockets
        self._PUSH_SOCKET = self._ZMQ_CONTEXT.socket(zmq.PUSH)
        self._PUSH_SOCKET.setsockopt(zmq.SNDHWM, 1)
        self._PUSH_SOCKET.setsockopt(zmq.LINGER, 0)
        
        self._PULL_SOCKET = self._ZMQ_CONTEXT.socket(zmq.PULL)
        self._PULL_SOCKET.setsockopt(zmq.RCVHWM, 1)
        self._PULL_SOCKET.setsockopt(zmq.LINGER, 0)

        self._PUB_SOCKET = self._ZMQ_CONTEXT.socket(zmq.PUB)
        self._PUB_SOCKET.setsockopt(zmq.SNDHWM, 1)
        self._PUB_SOCKET.setsockopt(zmq.LINGER, 0)

        # Initialize POLL set and register PULL and SUB sockets
        self._poller = zmq.Poller()
        self._poller.register(self._PULL_SOCKET, zmq.POLLIN)
        
        # Bind PUSH Socket to receive commands from MetaFarmerXConnector
        self._PUSH_SOCKET.bind(self._URL + str(self._PUSH_PORT))
        print("[INIT] Ready to send commands to MetaFarmerX (PUSH): " + str(self._PUSH_PORT))
        
        # Connect PULL Socket to send responses to MetaFarmerXConnector
        self._PULL_SOCKET.bind(self._URL + str(self._PULL_PORT))
        print("[INIT] Listening for responses from MetaFarmerX (PULL): " + str(self._PULL_PORT))
        
        # Connect PUB Socket to send market data to MetaFarmerXConnector
        print("[INIT] Listening for market data from MetaFarmerX (SUB): " + str(self._PUB_PORT))
        self._PUB_SOCKET.bind(self._URL + str(self._PUB_PORT))

        # Instantiate APIs
        self.price = CoinGeckoAdapter()
        self.farming_apy = HomoraAdapter()
        self.borrowing_apy = CreamAdapter()

        # Run server
        self._RUN = True
        # self._Server_Thread = Thread(target=self.RunServer, 
        #                                  args=(';',1000,))
        # self._Server_Thread.daemon = True
        # self._Server_Thread.start()
        self.RunServer()


    ##########################################################################    
    """
    Function to send data to Connector Client (PUSH)
    """
    def remote_send(self, _socket, _data):
        
        try:
            _socket.send_string(_data, zmq.DONTWAIT)
        except zmq.error.Again:
            print("\nResource timeout.. please try again.")
            sleep(self._sleep_delay)
      
    ##########################################################################
    """
    Function to retrieve commands from Connector (PULL)
    """
    def remote_recv(self, _socket):
        
        try:
            msg = _socket.recv_string(zmq.DONTWAIT)
            return msg
        except zmq.error.Again:
            print("\nResource timeout.. please try again.")
            sleep(self._sleep_delay)
        
        return None
        
    ##########################################################################
    """
    Function to send market data to subscribed client
    """
    def OnTick(self):
        if self._PUBLISH_MARKET_DATA == True:
            
            # get data
            self.price.call()
            self.farming_apy.call()
            self.borrowing_apy.call()

            msg = "{}: {};".format('Avalanche-2', self.borrowing_apy.call())

            print("Sending: ", msg)
            # send data
            self.remote_send(self._PUB_SOCKET, msg)

   ##########################################################################
    """
    Function to send market data to subscribed client
    """
    def MessageHandler(self, msg):
        
        #Get data from request   

        self.MessageParser()
      
        self.MessageInterpreter()

    ##########################################################################
    """
    Function to interpret data
    """
    def MessageInterpreter(self):
        pass

    ##########################################################################
    """
    Function to parse data
    """
    def MessageParser(self):
        pass

    ##########################################################################
    """
    Function to check Poller for new reponses (PULL) and market data (SUB)
    """
    def RunServer(self, string_delimiter=';', poll_timeout=1):
        
        while self._RUN:
            
            sleep(self._sleep_delay) # sleep() is s.
            
            sockets = dict(self._poller.poll(poll_timeout))
            
            # Process response to commands sent to MetaFarmerX
            if self._PULL_SOCKET in sockets and sockets[self._PULL_SOCKET] == zmq.POLLIN:
                
                try:
                    msg = self.remote_recv(self._PULL_SOCKET)
                    if msg != '' and msg != None:
                        try: 
                            _data = eval(msg)
                            self.MessageHandler(_data)
                                
                        except Exception as ex:
                            _exstr = "Exception Type {0}. Args:\n{1!r}"
                            _msg = _exstr.format(type(ex).__name__, ex.args)
                            print(_msg)
                
                except zmq.error.Again:
                    pass # resource temporarily unavailable, nothing to print
                except ValueError:
                    pass # No data returned, passing iteration.
                except UnboundLocalError:
                    pass # _symbol may sometimes get referenced before being assigned.
                
            self.OnTick()

    ##########################################################################
    """
    APIs to interact 
    """
    def MFX_Add_Liquidity(self):
        pass

    ##########################################################################
    """
    APIs to interact 
    """
    def MFX_Remove_Liquidity(self):
        pass

    ##########################################################################
    """
    APIs to interact 
    """
    def MFX_Harvest_Rewards(self):
        pass


def main():
    server = MetaFarmerXServer()

if __name__ == "__main__":
    main()