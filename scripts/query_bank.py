from brownie import Contract, config, interface

from .config_manager import get_abi


####################################################################### 
def query_pool(pos_id):
    """
    Query for pool data  
    """
    bank = Contract.from_abi("HomoraBank", config["alpha-homora"]["HomoraBank"], get_abi(config["alpha-homora"]["HomoraBankABI"]))
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

    return token0_supply, token1_supply

####################################################################### 
def query_bank(pos_id):
    """
    Query for debt data 
    """
    bank = Contract.from_abi("HomoraBank", config["alpha-homora"]["HomoraBank"], get_abi(config["alpha-homora"]["HomoraBankABI"]))
    _, collToken, collId, _ = bank.getPositionInfo(pos_id)
    pool = interface.IAny(collToken).getUnderlyingToken(collId)

    token0 = interface.IAny(pool).token0()
    token1 = interface.IAny(pool).token1()

    collateral_value = bank.getCollateralETHValue(pos_id)
    borrow_value = bank.getBorrowETHValue(pos_id)

    print(f'collateral value: {collateral_value}')
    print(f'borrow value: {borrow_value}')

    token0_debt = bank.borrowBalanceStored(pos_id, token0) / 10**interface.IAny(token0).decimals()
    token1_debt = bank.borrowBalanceStored(pos_id, token1) / 10**interface.IAny(token1).decimals()

    print(f'{interface.IAny(token0).symbol()} Debt:', token0_debt)
    print(f'{interface.IAny(token1).symbol()} Debt:', token1_debt)

    return collateral_value, borrow_value, token0_debt, token1_debt


def main():
    pos_id = int(input("Input positionID: "))
    query_bank(pos_id)
    query_pool(pos_id)

if __name__ == "__main__":
    main()
