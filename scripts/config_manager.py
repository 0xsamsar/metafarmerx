import json

from brownie import Contract, accounts, config, interface


########################## Global Variables ###########################  
MAX_INT = 2**256-1

####################################################################### 
def get_abi(abi):
    """
    Helper function to load abis
    """
    f = open("./abis/alpha-homora/{}".format(abi))
    return json.load(f)

####################################################################### 
def get_account():
    """
    Creates wallet account from private key
    """
    account = accounts.add(config["wallets"]["privateKey"])
    return account

####################################################################### 
def get_approvals(lp_pair, account):
    """
    Token approvals for AlphaHomora
    """
    bank = Contract.from_abi("HomoraBank", config["alpha-homora"]["HomoraBank"], get_abi(config["alpha-homora"]["HomoraBankABI"]))
    token0 = interface.IAny(config["alpha-homora"]["pools"][lp_pair]["token0"])
    token1 = interface.IAny(config["alpha-homora"]["pools"][lp_pair]["token1"])
    tokenLP = interface.IAny(config["alpha-homora"]["pools"][lp_pair]["tokenLP"])
    
    tx = token0.approve(bank, MAX_INT, {'from': account})
    tx.wait(1)
    tx = token1.approve(bank, MAX_INT, {'from': account})
    tx.wait(1)
    tx = tokenLP.approve(bank, MAX_INT, {'from': account})
    tx.wait(1)
    print("Approvals Granted!")


def main(lp_pair="USDC.e/AVAX"):
    account = get_account()
    get_approvals(lp_pair, account)

if __name__ == "__main__":
    main()