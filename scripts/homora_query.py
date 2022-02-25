from brownie import config, interface, Contract
from .utils import load_abi


def query_pool(pos_id):
    bank = Contract.from_abi("HomoraBank", config["alpha-homora"]["HomoraBank"], load_abi(config["alpha-homora"]["HomoraBankABI"]))
    _, collToken, collId, collSize = bank.getPositionInfo(pos_id)
    pool = interface.IAny(collToken).getUnderlyingToken(collId)

    r0, r1, _ = interface.IAny(pool).getReserves()
    supply = interface.IAny(pool).totalSupply()

    token0 = interface.IAny(pool).token0()
    token1 = interface.IAny(pool).token1()

    token0_supply = r0 * collSize // supply / 10**interface.IAny(token0).decimals()
    token1_supply = r1 * collSize // supply / 10**interface.IAny(token1).decimals()

    print(f'{interface.IAny(token0).symbol()} Supply:', token0_supply)
    print(f'{interface.IAny(token1).symbol()} Supply:', token1_supply)
    print(collSize)
    return token0_supply, token1_supply

    
def query_bank(pos_id):
    bank = Contract.from_abi("HomoraBank", config["alpha-homora"]["HomoraBank"], load_abi(config["alpha-homora"]["HomoraBankABI"]))
    collateral_value = bank.getCollateralETHValue(pos_id)
    borrow_value = bank.getBorrowETHValue(pos_id)

    print(f'collateral value: {collateral_value}')
    print(f'borrow value: {borrow_value}')

    return collateral_value, borrow_value


def main():
    pos_id = 8000 # random pos 
    query_pool(pos_id)
    query_bank(pos_id) 

if __name__ == "__main__":
    main()