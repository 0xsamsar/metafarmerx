import zmq
from time import sleep
from pandas import DataFrame, Timestamp
from threading import Thread


class BaseStrategy():
    """
    Base Yield Farming Strategy
    """
    def __init__(self, 
        _ClientID='mfx-client',    # Unique ID for this client
        _host='localhost',         # Host to connect to
        _protocol='tcp',           # Connection protocol
        _SUB_PORT=32770,           # Port for Subscribing for prices
        _delimiter=';',            # String delimiter
        _subdata_handlers = [],    # Handlers to process data received through SUB port.         
        _poll_timeout=1000,        # ZMQ Poller Timeout (ms)
        _sleep_delay=1):       # 1 ms for time.sleep()
    
        ######################################################################
        
        # Strategy Status (if this is False, ZeroMQ will not listen for data)
        self._ACTIVE = True
        
        # Client ID
        self._ClientID = _ClientID
        
        # ZeroMQ Host
        self._host = _host
        
        # Connection Protocol
        self._protocol = _protocol

        # ZeroMQ Context
        self._ZMQ_CONTEXT = zmq.Context()
        
        # TCP Connection URL Template
        self._URL = self._protocol + "://" + self._host + ":"
        
        # Handlers for received data (sub ports)
        self._subdata_handlers = _subdata_handlers

        # Ports for PUSH, PULL and SUB sockets respectively
        self._SUB_PORT = _SUB_PORT
        
        # Create Sockets
        self._SUB_SOCKET = self._ZMQ_CONTEXT.socket(zmq.SUB)
        
        # Connect SUB Socket to receive market data from MetaFarmerX
        print("[INIT] Listening for market data from MetaFarmerX (SUB): " + str(self._SUB_PORT))
        self._SUB_SOCKET.connect(self._URL + str(self._SUB_PORT))
        self._SUB_SOCKET.setsockopt_string(zmq.SUBSCRIBE, '')
        
        # Initialize POLL set and register SUB sockets
        self._poller = zmq.Poller()
        self._poller.register(self._SUB_SOCKET, zmq.POLLIN)
        
        # Start listening for responses to commands and new market data
        self._string_delimiter = _delimiter
        
        # Market Data Subscription Threads ({SYMBOL: Thread})
        self._MarketData_Thread = None
        
        # Market Data Dictionary by Symbol (holds price data)
        self._Market_Data_DB = {}   # {SYMBOL: {TIMESTAMP: PRICE}}
        
        # Position Data Dictionary by Position ID
        self._Position_Data_DB = {} 
                                
        # ZMQ Poller Timeout
        self._poll_timeout = _poll_timeout
        
        # Global Sleep Delay
        self._sleep_delay = _sleep_delay
        
        # Begin polling for SUB data
        # self._MarketData_Thread = Thread(target=self._MFX_Poll_Data_, 
        #                                  args=(self._string_delimiter,
        #                                        self._poll_timeout,))
        # self._MarketData_Thread.daemon = True
        # self._MarketData_Thread.start()
       
    ##########################################################################
    def _MFX_SHUTDOWN_(self):
        
        # Set INACTIVE
        self._ACTIVE = False
        
        # Get all threads to shutdown
        if self._MarketData_Thread is not None:
            self._MarketData_Thread.join()
        
        # Unregister sockets from Poller
        self._poller.unregister(self._SUB_SOCKET)
        print("\n++ [KERNEL] Sockets unregistered from ZMQ Poller()! ++")
        
        # Terminate context 
        self._ZMQ_CONTEXT.destroy(0)
        print("\n++ [KERNEL] ZeroMQ Context Terminated.. shut down safely complete! :)")
        
    ##########################################################################
    """
    Set Status (to enable/disable strategy manually)
    """
    def _setStatus(self, _new_status=False):
    
        self._ACTIVE = _new_status
        print("\n**\n[KERNEL] Setting Status to {} - Deactivating Threads.. please wait a bit.\n**".format(_new_status))
                
    ##########################################################################
    """
    Function to get output from thread
    """
    def _get_response_(self):
        return self._thread_data_output
    
    ##########################################################################
    """
    Function to set output from thread
    """
    def _set_response_(self, _resp=None):
        self._thread_data_output = _resp
    
    ##########################################################################
    """
    Function to retrieve data from MetaFarmerX (PULL)
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
    Liquidity Pool Helper Functions
    """

    # OPEN POSITION
    def _MFX_NEW_POSITION_(self, _position_id=0):
        pass

    # CLOSE POSITION
    def _MFX_CLOSE_POSITION_(self, _position_id):
        pass
            
    # ADD LIQUIDITY
    def _MFX_ADD_LIQUIDITY_(self, _position_id):
        pass
    
    # REMOVE LIQUIDITY
    def _MFX_REMOVE_LIQUIDITY_(self, _position_id):
        pass
        
    # GET OPEN POSITIONS
    def _MFX_GET_ALL_OPEN_POSITIONS_(self, _position_id):
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

            # Receive new market data from MetaFarmerX
            try:
                msg = self._SUB_SOCKET.recv_string(zmq.DONTWAIT)
                
                if msg != "":

                    _timestamp = str(Timestamp.now('UTC'))[:-6]
                    #print(msg)
                    # _symbol, _data = msg.split(self._main_string_delimiter)
                    # if len(_data.split(string_delimiter)) == 1:
                    #     _price = _data.split(string_delimiter)   
                                                                
                    
                    #     if self._verbose:
                    #         print("\n[" + _symbol + "] " + _timestamp + " (" + _price + ") USD")                    
                
                    #     # Update Market Data DB
                    #     if _symbol not in self._Market_Data_DB.keys():
                    #         self._Market_Data_DB[_symbol] = {}
                        
                    #     self._Market_Data_DB[_symbol][_timestamp] = (float(_price))

                    # elif len(_data.split(string_delimiter)) == 8:
                    #     _time, _open, _high, _low, _close, _tick_vol, _spread, _real_vol = _data.split(string_delimiter)
                    #     if self._verbose:
                    #         print("\n[" + _symbol + "] " + _timestamp + " (" + _time + "/" + _open + "/" + _high + "/" + _low + "/" + _close + "/" + _tick_vol + "/" + _spread + "/" + _real_vol + ") TIME/OPEN/HIGH/LOW/CLOSE/TICKVOL/SPREAD/VOLUME")                    
                    #     # Update Market Rate DB
                    #     if _symbol not in self._Market_Data_DB.keys():
                    #         self._Market_Data_DB[_symbol] = {}
                    #     self._Market_Data_DB[_symbol][_timestamp] = (int(_time), float(_price))

                    # invokes data handlers on sub port
                    for hnd in self._subdata_handlers:
                        hnd.onSubData(msg)

            except zmq.error.Again:
                pass # resource temporarily unavailable, nothing to print
            except ValueError:
                pass # No data returned, passing iteration.
            except UnboundLocalError:
                pass # _symbol may sometimes get referenced before being assigned.
                    
        print("\n++ [KERNEL] _MFX_Poll_Data_() Signing Out ++")
                

# def main():
#     strategy = BaseStrategy()
#     strategy._MFX_Poll_Data_()

# if __name__ == "__main__":
#     main()