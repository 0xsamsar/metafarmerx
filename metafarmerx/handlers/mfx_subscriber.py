import sys
import zmq
from time import sleep

from pandas import DataFrame, Timestamp


class MFXSubscriber(object):
    """
    Subscribes stratgies to real-time market data from MetaFarmerX
    """
    def __init__(self,
                _host='localhost',
                _protocol='tcp', 
                _sub_port=42069,
                _subdata_handlers=[], 
                _multiprocess=True):
        # Strategy Status 
        self._ACTIVE = True
        
        # ZeroMQ Host
        self._host = _host
        
        # Connection Protocol
        self._protocol = _protocol

        # TCP Connection URL Template
        self._url = self._protocol + "://" + self._host + ":"
        
        # Data Handlers  
        self._subdata_handlers = _subdata_handlers

        # SUB Sockets Port
        self._sub_port = _sub_port

        self._multiprocess = _multiprocess
        
        if self._multiprocess == False:
            self.create_context()
                     
        # Global Sleep Delay (s)
        self._sleep_delay = 1

        # Timing Variables
        self._prev_msg_timestamp = {}
       
    ##########################################################################
    def create_context(self):
        """
        Creates ZeroMQ Context
        """
        # ZeroMQ Context
        self._zmq_context = zmq.Context()

        # Create Sockets
        self._sub_socket = self._zmq_context.socket(zmq.SUB)

        # Connect SUB Socket to MetaFarmerX
        self._sub_socket.connect(self._url + str(self._sub_port))
        self._sub_socket.setsockopt_string(zmq.SUBSCRIBE, '')
        print("[SUCCESS] Listening for market data [SUB]: " + str(self._sub_port))
    
    ##########################################################################
    def shutdown(self):
        """
        Terminate strategy safely
        """
        # Set INACTIVE
        self._ACTIVE = False
                
        # Terminate context 
        self._zmq_context.destroy(0)
        print("\n++ [INFO] Strategy safely terminated")
        
    ##########################################################################
    def set_status(self, _new_status=False):
        """
        Set Status (to enable/disable strategy manually)
        """
        self._ACTIVE = _new_status
        print("\n**\n[INFO] Setting Status to {} \n**".format(_new_status))
                
    ##########################################################################
    def set_sleep_delay(self, delay):
        """
        Set new sleep delay
        """
        self._sleep_delay = delay
    
    ##########################################################################
    def poll(self):
        """
        Subscribe and monitor market data
        """
        if self._multiprocess:
            self.create_context()

        while self._ACTIVE:
            sleep(self._sleep_delay) 
            # Receive new market data from MetaFarmerX

            try:
                msg = self._sub_socket.recv_json(zmq.DONTWAIT)
                
                if msg != "":
                    self._prev_msg_timestamp['time'] = str(Timestamp.now('UTC'))[:-6]

                    # invoke data handlers 
                    for handler in self._subdata_handlers:
                        handler.on_market_data(msg)

            except zmq.error.Again:
                pass # resource temporarily unavailable
            except ValueError:
                pass # No data returned
            except UnboundLocalError:
                pass 
                         
