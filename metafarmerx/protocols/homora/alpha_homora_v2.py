from brownie import accounts, config, Contract, interface

from .traderjoe_spell import TraderJoeSpell
from .utils import load_abi

class AlphaHomoraV2(object):
    """
    Controller for interacting with leveraged yield farms
    """
    def __init__(self, _spell_name, _pool, _account):
        self._account = _account
        self._spell_name = _spell_name
        self._pool = _pool
        self._bank = Contract.from_abi("HomoraBank", config["alpha-homora"]["HomoraBank"], 
                                                        load_abi(config["alpha-homora"]["HomoraBankABI"]))
        self._spell = Contract.from_abi(self._spell, config["alpha-homora"]["pools"][self._pool]["spell"], 
                                                        load_abi(config["alpha-homora"]["pools"][self._pool]["spellAbi"]))

        #TODO: Use a Factory design pattern to decouple dependency 
        self._amm = TraderJoeSpell(self._pool, self._bank, self._spell)

    ##########################################################################    
    #TODO Debug 'interface' import error
    def query_pool(self, pos_id):
        """
        Query token supplies in LP
        """
        _, collToken, collId, collSize = self._bank.getPositionInfo(pos_id)
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

    ##########################################################################    
    def query_bank(self, pos_id):
        """
        Query HomoraBank for position info
        """
        collateral_value = self._bank.getCollateralETHValue(pos_id)
        borrow_value = self._bank.getBorrowETHValue(pos_id)

        print(f'collateral value: {collateral_value}')
        print(f'borrow value: {borrow_value}')

        return collateral_value, borrow_value

    ##########################################################################        
    def add_liquidity(self, pos_id, call_data):
        """
        Add liquidity to lp
        """
        return self._amm.add_liquidity(pos_id, call_data)

    ##########################################################################
    def remove_liquidity(self, pos_id, call_data):
        """
        Remove liquidity from lp
        """
        return self._amm.remove_liquidity(pos_id, call_data)

    ##########################################################################
    def harvest_rewards(self, pos_id):
        """
        Harvest rewards
        """
        return self._amm.harvest_rewards(self, pos_id)
