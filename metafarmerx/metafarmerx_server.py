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
        _ServerID='mfx-server',    # Unique ID for this client
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

        # Set Configuration
        self._MILLISECOND_TIMER = 1
        self._MILLISECOND_TIMER_PRICES = 500
        self._MAIN_STRING_DELIMITER = ":|:"

        # Market Data Client Configuration
        self._PUBLISH_MARKET_DATA = False
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
        self._PUSH_SOCKET.connect(self._URL + str(self._PUSH_PORT))
        print("[INIT] Ready to send commands to MetaFarmerX (PUSH): " + str(self._PUSH_PORT))
        
        # Connect PULL Socket to send responses to MetaFarmerXConnector
        self._PULL_SOCKET.connect(self._URL + str(self._PULL_PORT))
        print("[INIT] Listening for responses from MetaFarmerX (PULL): " + str(self._PULL_PORT))
        
        # Connect PUB Socket to send market data to MetaFarmerXConnector
        print("[INIT] Listening for market data from MetaFarmerX (SUB): " + str(self._PUB_PORT))
        self._SUB_SOCKET.connect(self._URL + str(self._PUB_PORT))
        
    ##########################################################################    
    """
    Function to send data to Connector Client (PUSH)
    """
    def remote_send(self, _socket, _data):
        
        if self._PUSH_SOCKET_STATUS['state'] == True:
            try:
                _socket.send_string(_data, zmq.DONTWAIT)
            except zmq.error.Again:
                print("\nResource timeout.. please try again.")
                sleep(self._sleep_delay)
        else:
            print('\n[KERNEL] NO HANDSHAKE ON PUSH SOCKET.. Cannot SEND data')
      
    ##########################################################################
    """
    Function to retrieve commands from Connector (PULL)
    """
    def remote_recv(self, _socket):
        
        if self._PULL_SOCKET_STATUS['state'] == True:
            try:
                msg = _socket.recv_string(zmq.DONTWAIT)
                return msg
            except zmq.error.Again:
                print("\nResource timeout.. please try again.")
                sleep(self._sleep_delay)
        else:
            print('\r[KERNEL] NO HANDSHAKE ON PULL SOCKET.. Cannot READ data', end='', flush=True)
            
        return None
        
    ##########################################################################
    """
    Function to send market data to subscribed client
    """
    def OnTick(self):
        if self._PUBLISH_MARKET_DATA == True:
            
            #get data

            #send data

            pass

   ##########################################################################
    """
    Function to send market data to subscribed client
    """
    def OnTimer(self):
        self.MessageHandler

        #send response

        onTick

   ##########################################################################
    """
    Function to send market data to subscribed client
    """
    def MessageHandler(self):
        
        #Get data from request   

        self.MessageParser()
      
        self.MessageInterpreter()

    ##########################################################################
    """
    Function to send market data to subscribed client
    """
    def MessageInterpreter(self):
        pass

    ##########################################################################
    """
    Function to send market data to subscribed client
    """
    def MessageParser(self):
        pass

    ##########################################################################
    """
    Function to check Poller for new reponses (PULL) and market data (SUB)
    """
    def _MFX_Poll_Data_(self, 
                           string_delimiter=';',
                           poll_timeout=1000):
        
        while self._ACTIVE:
            
            sleep(self._sleep_delay) # poll timeout is in ms, sleep() is s.
            
            sockets = dict(self._poller.poll(poll_timeout))
            
            # Process response to commands sent to MetaFarmerX
            if self._PULL_SOCKET in sockets and sockets[self._PULL_SOCKET] == zmq.POLLIN:
                
                if self._PULL_SOCKET_STATUS['state'] == True:
                    try:
                        
                        # msg = self._PULL_SOCKET.recv_string(zmq.DONTWAIT)
                        msg = self.remote_recv(self._PULL_SOCKET)
                        
                        # If data is returned, store as pandas Series
                        if msg != '' and msg != None:
                            
                            try: 
                                _data = eval(msg)
                                if '_action' in _data and _data['_action'] == 'HIST':
                                    _symbol = _data['_symbol']
                                    if '_data' in _data.keys():
                                        if _symbol not in self._History_DB.keys():
                                            self._History_DB[_symbol] = {}
                                        self._History_DB[_symbol] = _data['_data']
                                    else:
                                        print('No data found.')
                                        print('message: ' + msg)
                                
                                # invokes data handlers on pull port
                                for hnd in self._pulldata_handlers:
                                    hnd.onPullData(_data)
                                
                                self._thread_data_output = _data
                                if self._verbose:
                                    print(_data) # default logic
                                    
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
                
                else:
                    print('\r[KERNEL] NO HANDSHAKE on PULL SOCKET.. Cannot READ data.', end='', flush=True)
                
        print("\n++ [KERNEL] _MFX_Poll_Data_() Signing Out ++")



    ##########################################################################
    """
    APIs to interact 
    """
    def MFX_Add_Liquidity(self):
        pass