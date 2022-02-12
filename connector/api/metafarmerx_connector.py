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


class MetaFarmerXConnector():

    """
    MetaFarmerX Connector
    """
    def __init__(self, 
        _ClientID='mfx-client',    # Unique ID for this client
        _host='localhost',         # Host to connect to
        _protocol='tcp',           # Connection protocol
        _PUSH_PORT=32768,          # Port for Sending commands
        _PULL_PORT=32769,          # Port for Receiving responses
        _SUB_PORT=32770,           # Port for Subscribing for prices
        _delimiter=';',            # String delimiter
        _pulldata_handlers = [],   # Handlers to process data received through PULL port.
        _subdata_handlers = [],    # Handlers to process data received through SUB port.
        _verbose=True,             
        _poll_timeout=1000,        # ZMQ Poller Timeout (ms)
        _sleep_delay=0.001,        # 1 ms for time.sleep()
        _monitor=False):           # Experimental ZeroMQ Socket Monitoring
    
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
        
        # Handlers for received data (pull and sub ports)
        self._pulldata_handlers = _pulldata_handlers
        self._subdata_handlers = _subdata_handlers

        # Ports for PUSH, PULL and SUB sockets respectively
        self._PUSH_PORT = _PUSH_PORT
        self._PULL_PORT = _PULL_PORT
        self._SUB_PORT = _SUB_PORT
        
        # Create Sockets
        self._PUSH_SOCKET = self._ZMQ_CONTEXT.socket(zmq.PUSH)
        self._PUSH_SOCKET.setsockopt(zmq.SNDHWM, 1)        
        self._PUSH_SOCKET_STATUS = {'state': True, 'latest_event': 'N/A'}
        
        self._PULL_SOCKET = self._ZMQ_CONTEXT.socket(zmq.PULL)
        self._PULL_SOCKET.setsockopt(zmq.RCVHWM, 1)
        self._PULL_SOCKET_STATUS = {'state': True, 'latest_event': 'N/A'}
        
        self._SUB_SOCKET = self._ZMQ_CONTEXT.socket(zmq.SUB)
        
        # Bind PUSH Socket to send commands to MetaFarmerX
        self._PUSH_SOCKET.connect(self._URL + str(self._PUSH_PORT))
        print("[INIT] Ready to send commands to MetaFarmerX (PUSH): " + str(self._PUSH_PORT))
        
        # Connect PULL Socket to receive command responses from MetaFarmerX
        self._PULL_SOCKET.connect(self._URL + str(self._PULL_PORT))
        print("[INIT] Listening for responses from MetaFarmerX (PULL): " + str(self._PULL_PORT))
        
        # Connect SUB Socket to receive market data from MetaFarmerX
        print("[INIT] Listening for market data from MetaFarmerX (SUB): " + str(self._SUB_PORT))
        self._SUB_SOCKET.connect(self._URL + str(self._SUB_PORT))
        
        # Initialize POLL set and register PULL and SUB sockets
        self._poller = zmq.Poller()
        self._poller.register(self._PULL_SOCKET, zmq.POLLIN)
        self._poller.register(self._SUB_SOCKET, zmq.POLLIN)
        
        # Start listening for responses to commands and new market data
        self._string_delimiter = _delimiter
        
        self._main_string_delimiter = ':|:'
        
        # Market Data Subscription Threads ({SYMBOL: Thread})
        self._MarketData_Thread = None
        
        # Socket Monitor Threads
        self._PUSH_Monitor_Thread = None
        self._PULL_Monitor_Thread = None
        
        # Market Data Dictionary by Symbol (holds price data)
        self._Market_Data_DB = {}   # {SYMBOL: {TIMESTAMP: PRICE}}
        
        # Position Data Dictionary by Position ID
        self._History_DB = {} 
                                
        # Temporary Order STRUCT for convenience wrappers later.
        self.temp_order_dict = self._generate_default_order_dict()
        
        # Verbosity
        self._verbose = _verbose
        
        # ZMQ Poller Timeout
        self._poll_timeout = _poll_timeout
        
        # Global Sleep Delay
        self._sleep_delay = _sleep_delay
        
        # Begin polling for PULL / SUB data
        self._MarketData_Thread = Thread(target=self._MFX_Poll_Data_, 
                                         args=(self._string_delimiter,
                                               self._poll_timeout,))
        self._MarketData_Thread.daemon = True
        self._MarketData_Thread.start()
       
    ##########################################################################
    def _MFX_SHUTDOWN_(self):
        
        # Set INACTIVE
        self._ACTIVE = False
        
        # Get all threads to shutdown
        if self._MarketData_Thread is not None:
            self._MarketData_Thread.join()
            
        if self._PUSH_Monitor_Thread is not None:
            self._PUSH_Monitor_Thread.join()
            
        if self._PULL_Monitor_Thread is not None:            
            self._PULL_Monitor_Thread.join()
        
        # Unregister sockets from Poller
        self._poller.unregister(self._PULL_SOCKET)
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
    Function to send commands to MetaFarmerX (PUSH)
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
    def _MFX_NEW_POSITION_(self, _order=None):
        
        if _order is None:
            _order = self._generate_default_order_dict()
        
        # Execute
        self._MFX_SEND_COMMAND_(**_order)
        
    # CLOSE POSITION
    def _MFX_CLOSE_POSITION_(self, _position_id):
        
        try:
            self.temp_order_dict['_action'] = 'CLOSE'
            self.temp_order_dict['_position_id'] = _position_id
            
            # Execute
            self._MFX_SEND_COMMAND_(**self.temp_order_dict)
            
        except KeyError:
            print("[ERROR] Position {} not found!".format(_position_id))
            
    # ADD LIQUIDITY
    def _MFX_ADD_LIQUIDITY_(self, _position_id):
        
        try:
            self.temp_order_dict['_action'] = 'ADD_LIQUIDITY'
            self.temp_order_dict['_position_id'] = _position_id
            
            # Execute
            self._MFX_SEND_COMMAND_(**self.temp_order_dict)
            
        except KeyError:
            print("[ERROR] Position {} not found!".format(_position_id))
    
    # REMOVE LIQUIDITY
    def _MFX_REMOVE_LIQUIDITY_(self, _position_id):
        
        try:
            self.temp_order_dict['_action'] = 'REMOVE_LIQUIDITY'
            self.temp_order_dict['_position_id'] = _position_id
            
            # Execute
            self._MFX_SEND_COMMAND_(**self.temp_order_dict)
            
        except KeyError:
            print("[ERROR] Position {} not found!".format(_position_id))
        
    # GET OPEN POSITIONS
    def _MFX_GET_ALL_OPEN_POSITIONS_(self, _position_id):
        
        try:
            self.temp_order_dict['_action'] = 'GET_OPEN_POSITIONS'
            self.temp_order_dict['_position_id'] = _position_id
            
            # Execute
            self._MFX_SEND_COMMAND_(**self.temp_order_dict)
            
        except KeyError:
            print("[ERROR] Position {} not found!".format(_position_id))
    
    # DEFAULT ORDER DICT
    def _generate_default_order_dict(self):
        return({'_action': 'OPEN', '_position_id': 0,
                                '_symbol': 'avalanche-2',
                                '_call_data': []})
    
    ##########################################################################
    """
    Request real-time price updates from MetaFarmerX 
    """
    def _MFX_SEND_TRACKPRICES_REQUEST_(self,
                                 _symbols=['avalanche-2']):
        _msg = 'TRACK_PRICES'
        for s in _symbols:
          _msg = _msg + ";{}".format(s)

        # Send via PUSH Socket
        self.remote_send(self._PUSH_SOCKET, _msg)
    
    ##########################################################################
    """
    Function to construct messages for sending Farming commands to MetaFarmerX
    """
    def _MFX_SEND_COMMAND_(self, _action='OPEN', _position_id=0,
                                _symbol='avalanche-2', 
                                _call_data=[]):
        
        _msg = "{};{};{};{};{}".format('TRADE',_action,_position_id,
                                                _call_data,_symbol)
        
        # Send via PUSH Socket
        self.remote_send(self._PUSH_SOCKET, _msg)
        
        """
         [0] = FARM | MARKET_DATA | POSITION_INFO
         [1] = ACTION (e.g. OPEN, CLOSE, ADD_LIQUIDITY, REMOVE_LIQUIDITY, HARVEST)
         [2] = POSITION_ID
         [3] = Symbol (e.g. AVALANCHE-2, etc.)
         [4] = CALL_DATA 
         """
    
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
            
            # Receive new market data from MetaFarmerX
            if self._SUB_SOCKET in sockets and sockets[self._SUB_SOCKET] == zmq.POLLIN:
                
                try:
                    msg = self._SUB_SOCKET.recv_string(zmq.DONTWAIT)
                    
                    if msg != "":

                        _timestamp = str(Timestamp.now('UTC'))[:-6]
                        _symbol, _data = msg.split(self._main_string_delimiter)
                        if len(_data.split(string_delimiter)) == 1:
                            _price = _data.split(string_delimiter)   
                                                                   
                        
                            if self._verbose:
                                print("\n[" + _symbol + "] " + _timestamp + " (" + _price + ") USD")                    
                    
                            # Update Market Data DB
                            if _symbol not in self._Market_Data_DB.keys():
                                self._Market_Data_DB[_symbol] = {}
                            
                            self._Market_Data_DB[_symbol][_timestamp] = (float(_price))

                        elif len(_data.split(string_delimiter)) == 8:
                            _time, _open, _high, _low, _close, _tick_vol, _spread, _real_vol = _data.split(string_delimiter)
                            if self._verbose:
                                print("\n[" + _symbol + "] " + _timestamp + " (" + _time + "/" + _open + "/" + _high + "/" + _low + "/" + _close + "/" + _tick_vol + "/" + _spread + "/" + _real_vol + ") TIME/OPEN/HIGH/LOW/CLOSE/TICKVOL/SPREAD/VOLUME")                    
                            # Update Market Rate DB
                            if _symbol not in self._Market_Data_DB.keys():
                                self._Market_Data_DB[_symbol] = {}
                            self._Market_Data_DB[_symbol][_timestamp] = (int(_time), float(_price))

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
                
    ##########################################################################
    """
    Function to subscribe to given Symbol's price feed from MetaFarmerX
    """
    def _MFX_SUBSCRIBE_MARKETDATA_(self, _symbol='avalanche-2'):
        
        # Subscribe to SYMBOL first.
        self._SUB_SOCKET.setsockopt_string(zmq.SUBSCRIBE, _symbol)
        
        print("[KERNEL] Subscribed to {} Price updates. See self._Market_Data_DB.".format(_symbol))
    
    """
    Function to unsubscribe to given Symbol's Price feed from MetaFarmerX
    """
    def _MFX_UNSUBSCRIBE_MARKETDATA_(self, _symbol):
        
        self._SUB_SOCKET.setsockopt_string(zmq.UNSUBSCRIBE, _symbol)
        print("\n**\n[KERNEL] Unsubscribing from " + _symbol + "\n**\n")
        
    """
    Function to unsubscribe from ALL MetaFarmerX Symbols
    """
    def _MFX_UNSUBSCRIBE_ALL_MARKETDATA_REQUESTS_(self):
        
        for _symbol in self._Market_Data_DB.keys():
            self._MFX_UNSUBSCRIBE_MARKETDATA_(_symbol=_symbol)
            

##############################################################################
"""
Function to Deinitialize the connector client safely
"""
def _MFX_CLEANUP_(_name='MFX_Connector',
                      _globals=globals(), 
                      _locals=locals()):
    
    print('\n++ [KERNEL] Initializing ZeroMQ Cleanup.. if nothing appears below, no cleanup is necessary, otherwise please wait..')
    try:
        _class = _globals[_name]
        _locals = list(_locals.items())
        
        for _func, _instance in _locals:
            if isinstance(_instance, _class): 
                print(f'\n++ [KERNEL] Found & Destroying {_func} object before __init__()')
                eval(_func)._MFX_SHUTDOWN_()
                print('\n++ [KERNEL] Cleanup Complete -> OK to initialize MFX_Connector if NETSTAT diagnostics == True. ++\n')
           
    except Exception as ex:
        
        _exstr = "Exception Type {0}. Args:\n{1!r}"
        _msg = _exstr.format(type(ex).__name__, ex.args)
            
        if 'KeyError' in _msg:
            print('\n++ [KERNEL] Cleanup Complete -> OK to initialize MFX_Connector. ++\n')
        else:
            print(_msg)


def main():
    pass


if __name__ == "__main__":
    main()