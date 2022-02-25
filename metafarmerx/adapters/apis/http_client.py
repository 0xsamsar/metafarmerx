import urllib3
import json
import requests


class HTTPClient(object):
    """
    Wraps HTTP Client with custom filtering
    """
    def __init__(self, _uri='', _query={}, _filter=True, _filter_keys=[]):
        self._uri = _uri
        self._query = _query
        self._timeout = 5

        self._filter = _filter
        self._filter_keys = _filter_keys
        self._response_json = {}

    ##########################################################################    
    def get_response(self):
        """
        Get response 
        """
        return self._response_json

    ##########################################################################    
    def filter_response(self):
        """
        Filter response by accesing key pairs in the json object
        """
        if self._filter:
            json_obj = self._response_json 
            for key in self._filter_keys:
                json_obj = json_obj[key]
            
            self._response_json = json.dumps(json_obj)

    ##########################################################################    
    def send_request(self):
        """
        Send HTTP request
        """
        try:
            self._response = requests.get(self._uri, params=self._query, timeout=self._timeout)
            self._response_json = self._response.json()
            self._response.raise_for_status()
        
        except requests.exceptions.HTTPError as errh:
            print(errh)
        
        except requests.exceptions.ConnectionError as errc:
            print(errc)
        
        except requests.exceptions.Timeout as errt:
            print(errt)
        
        except requests.exceptions.RequestException as err:
            print(err)

    ##########################################################################    
    def call(self):
        """
        Call the API
        """  
        self.send_request()
        self.filter_response()
        self._response.close()



