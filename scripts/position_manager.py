import json
import sys

sys.path.append("./metafarmerx")

from adapters.apis.coingecko_adapter import CoinGeckoAdapter
from brownie import Contract, config, network, accounts
from brownie.network import transaction
from controllers.protocols.alpha_homora_v2.alpha_homora_v2 import AlphaHomoraV2
from .config_manager import get_account


########################## Global Variables ###########################  
MAX_INT = 2**256-1

####################################################################### 
def open_position(lp_pair, leverage, supply_amt, account):
    """
    Open delta neutral position
    """
    pos_id = 0
    risky_token = config["alpha-homora"]["pools"][lp_pair]["riskyTokenCGID"]

    protocol = AlphaHomoraV2(pos_id, lp_pair, account)
    coingecko = CoinGeckoAdapter()
    
    coingecko.call()
    risky_token_price = json.loads(coingecko.get_response())

    stable_borrow_amt = supply_amt / (leverage-1)
    risky_borrow_amt = supply_amt * (leverage/2)
    risky_borrow_amt = risky_borrow_amt / float(risky_token_price[risky_token]["usd"])

    call_data = [
                    supply_amt * 10**6,         # supply USDC.e
                    0,                          # supply AVAX
                    0,                          # supply LP
                    stable_borrow_amt * 10**6,  # borrow USDC.e
                    risky_borrow_amt * 10**18,  # borrow AVAX
                    0,                          # borrow LP tokens
                    0,                          # min USDC
                    0                           # min AVAX
                ]

    try:
        pos_tx = protocol.add_liquidity(pos_id, call_data)
    except:
        sys.exit('Failed to create delta neutral position')

    pos_id = pos_tx.events["Execute"]["positionId"]
    print("PositionID: ", pos_id)
    
    return pos_id, stable_borrow_amt, risky_borrow_amt

####################################################################### 
def close_position(account, lp_pair, pos_id):
    """
    Close position
    """
    protocol = AlphaHomoraV2(pos_id, lp_pair, account)

    call_data = [        
                    MAX_INT,        # take out LP tokens
                    0,              # withdraw LP tokens to wallet
                    MAX_INT,        # repay USDC
                    MAX_INT,        # repay AVAX
                    0,              # repay LP
                    0,              # min USDC
                    0               # min AVAX
                ]
    try:
        pos_tx = protocol.remove_liquidity(pos_id, call_data)
    except:
        sys.exit('Failed to close positions')

    return pos_tx

####################################################################### 
def harvest_rewards(account, lp_pair, pos_id):
    """
    Harvest Rewards
    """
    #TODO: 
    pass


def main(lp_pair="USDC.e/AVAX"):
    account = get_account()
    pos_id = input("Input positionID to close position: ")

    close_position(account, lp_pair, pos_id)

if __name__ == "__main__":
    main()
