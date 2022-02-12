import json
from web3 import Web3
from brownie import accounts, config, Contract
from ..scripts.utils import load_abi, get_account
from ..scripts.traderjoe_spell import add_liquidity, remove_liquidity


def test_open_position():
    pos_id = 0
    call_data = [
                    50 * 10**6,     # supply USDC.e
                    0,              # supply AVAX
                    0,              # supply LP
                    100 * 10**6,    # borrow USDC.e
                    0,              # borrow AVAX
                    0,              # borrow LP tokens
                    0,              # min USDC
                    0               # min AVAX
                ]
    add_liquidity(pos_id, call_data)

def test_close_position(pos_id):
    call_data = [        
                    2**256-1,       # take out LP tokens
                    0,              # withdraw LP tokens to wallet
                    2**256-1,       # repay USDC
                    2**256-1,       # repay AVAX
                    0,              # repay LP
                    0,              # min USDC
                    0               # min AVAX
                ],
    remove_liquidity(pos_id, call_data)

def test_add_collateral():
    pass

def test_remove_collaterall():
    pass

def test_harvest_rewards():
    pass

#TODO: Create test cases for all contract transactions
def main():
    test_open_position()


if __name__ == "main":
    main()