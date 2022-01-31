from brownie import  config, interface, Contract
from .utils import load_abi


def get_position_data(pos_id):
    bank = Contract.from_abi("HomoraBank", config["alpha-homora"]["HomoraBank"], load_abi(config["alpha-homora"]["HomoraBankABI"]))
    _, collToken, collId, collSize = bank.getPositionInfo(pos_id)
    pool = interface.IAny(collToken).getUnderlyingToken(collId)

    r0, r1, _ = interface.IAny(pool).getReserves()
    supply = interface.IAny(pool).totalSupply()

    token0 = interface.IAny(pool).token0()
    token1 = interface.IAny(pool).token1()
    
    token0_supply =  r0 / 10**interface.IAny(token0).decimals()
    token1_supply = r1 / 10**interface.IAny(token1).decimals()

    print(f'{interface.IAny(token0).symbol()} amount:', r0 * collSize // supply / 10**interface.IAny(token0).decimals())
    print(f'{interface.IAny(token1).symbol()} amount:', r1 * collSize // supply / 10**interface.IAny(token1).decimals())

#TODO: Need to be flash loan proof
def get_oracle_price_data():
    pass

