import json
from brownie import accounts, config


def load_abi(abi):
    f = open("./abis/{}".format(abi))
    return json.load(f)

def get_account():
    account = accounts.add(config["wallets"]["private_key"])
    return account