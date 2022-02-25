import json
from brownie import accounts, config


def load_abi(abi):
    f = open("./abis/alpha-homora/{}".format(abi))
    return json.load(f)

def get_account():
    account = accounts.add(config["wallets"]["privateKey"])
    return account
