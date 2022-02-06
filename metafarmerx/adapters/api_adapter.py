import json
import requests


class APIBaseAdapter:
    def __init__(self):
        self.endpoint = ''
        self.json_filter = []
        self.timeout = 5
    
    def get_response(self):
        response = self.response.json()
        if len(self.json_filter) == 0:  return response
        obj = response 
        for key in self.json_filter:
            obj = obj[key]
        return obj

    def request(self):
        try:
            self.response = requests.get(self.endpoint, timeout=self.timeout)
            self.response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print(errh)
        except requests.exceptions.ConnectionError as errc:
            print(errc)
        except requests.exceptions.Timeout as errt:
            print(errt)
        except requests.exceptions.RequestException as err:
            print(err)

    def call(self):
        self.request()
        result = self.get_response()
        self.response.close()
        return result


class CoinGeckoAdapter(APIBaseAdapter):
    def __init__(self):
        super().__init__()
        self.endpoint = 'https://api.coingecko.com/api/v3/simple/price?ids=avalanche-2,alpha-finance,joe&vs_currencies=usd'
        self.json_filter = ['avalanche-2']


class HomoraAdapter(APIBaseAdapter):
    def __init__(self):
        super().__init__()
        self.endpoint = 'https://homora-api.alphafinance.io/v2/43114/apys'
        self.json_filter = ['wchef-0xb41de9c1f50697cc3fd63f24ede2b40f6269cbcb-39']


class CreamAdapter(APIBaseAdapter):
    def __init__(self):
        super().__init__()
        self.endpoint = 'https://api.cream.finance/api/v1/crtoken?comptroller=avalanche'
        self.json_filter = ['iWAVAX','iUSDT.E','iUSDC.E','iDAI.E']

    # get the borrow apy for selected tokens
    def get_response(self):
        response = self.response.json()
        result = {'iWAVAX':0.0,'iUSDT.E':0.0,'iUSDC.E':0.0,'iDAI.E':0.0}
        for key in response:
            if key['symbol'] in self.json_filter:
                result[key['symbol']] = float(key["borrow_apy"]["value"]) 
        return json.dumps(result)

