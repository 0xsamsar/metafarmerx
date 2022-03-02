import sys

from brownie import Contract, accounts, config, interface
from scripts.config_manager import get_abi

from .traderjoe_spell import TraderJoeSpell


class AlphaHomoraV2(object):
    """
    Controller for interacting with leveraged yield farms
    """
    def __init__(self, _pos_id, _lp_pair, _account):
        self._pos_id = _pos_id
        self._lp_pair = _lp_pair
        self._account = _account
        
        self._spell_name = config["alpha-homora"]["pools"][self._lp_pair]["spellName"]
        self._bank = Contract.from_abi("HomoraBank", config["alpha-homora"]["HomoraBank"], 
                                                        get_abi(config["alpha-homora"]["HomoraBankABI"]))

        self._spell = Contract.from_abi(self._spell_name, config["alpha-homora"]["pools"][self._lp_pair]["spell"], 
                                                        get_abi(config["alpha-homora"]["pools"][self._lp_pair]["spellAbi"]))

        self._spell_name = config["alpha-homora"]["pools"][self._lp_pair]["spellName"]
        
        if self._spell_name == "TraderJoeSpellV1":
            self._amm = TraderJoeSpell(self._lp_pair, self._bank, self._spell, self._account)
        
        #TODO: Implement PangolinSpell Controller
        elif self._spell_name == "PangolinSpellV2":
            sys.exit('Spell not integrated yet')

        else:
            sys.exit('Error loading spell...')

    ##########################################################################    
    def query_pool(self, pos_id):
        """
        Query token supplies in LP
        """
        _, coll_token, coll_id, coll_size = self._bank.getPositionInfo(pos_id)
        pool = interface.IAny(coll_token).getUnderlyingToken(coll_id)
        r0, r1, _ = interface.IAny(pool).getReserves()
        supply = interface.IAny(pool).totalSupply()

        token0 = interface.IAny(pool).token0()
        token1 = interface.IAny(pool).token1()

        token0_supply = r0 * coll_size // supply / 10**interface.IAny(token0).decimals()
        token1_supply = r1 * coll_size // supply / 10**interface.IAny(token1).decimals()

        return token0_supply, token1_supply

    ##########################################################################    
    def query_bank(self, pos_id):
        """
        Query HomoraBank for debt info
        """
        _, coll_token, coll_id, _ = self._bank.getPositionInfo(pos_id)
        pool = interface.IAny(coll_token).getUnderlyingToken(coll_id)
        
        collateral_value = self._bank.getCollateralETHValue(pos_id)
        borrow_value = self._bank.getBorrowETHValue(pos_id)

        token0 = interface.IAny(pool).token0()
        token1 = interface.IAny(pool).token1()

        token0_debt = self._bank.borrowBalanceStored(pos_id, token0) / 10**interface.IAny(token0).decimals()
        token1_debt = self._bank.borrowBalanceStored(pos_id, token1) / 10**interface.IAny(token1).decimals()

        return collateral_value, borrow_value, token0_debt, token1_debt

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
        return self._amm.harvest_rewards(pos_id)
