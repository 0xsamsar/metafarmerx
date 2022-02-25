import json

def load_abi(abi):
    f = open("../../../abis/alpha-homora{}".format(abi))
    return json.load(f)
