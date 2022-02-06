import json
from brownie import accounts, config, interface


def load_abi(abi):
    f = open("./abis/{}".format(abi))
    return json.load(f)

def get_account():
    account = accounts.add(config["wallets"]["privateKey"])
    return account

def calculate_borrow_apy(borrow_rate):
    blocks_per_day = 6570 # (13.15 seconds per block)
    borrow_apy = ((((borrow_rate * blocks_per_day) + 1)**365)-1)*100
    return borrow_apy