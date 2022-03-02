from brownie import config, Contract, accounts


class TraderJoeSpell(object):
    """
    AMM Controller
    """
    def __init__(self, _lp_pair, _bank, _spell, _account):
        self._lp_pair = _lp_pair
        self._bank = _bank
        self._spell = _spell
        self._account = _account

    ##########################################################################        
    def add_liquidity(self, pos_id, call_data):
        """
        Add liquidity to lp
        """
        tx = self._bank.execute(
            pos_id,
            self._spell,
            self._spell.addLiquidityWERC20.encode_input(
                config["alpha-homora"]["pools"][self._lp_pair]["token0"],  
                config["alpha-homora"]["pools"][self._lp_pair]["token1"],  
                call_data,  
            ),
            {'from': self._account}
        )
        return tx

    ##########################################################################
    def remove_liquidity(self, pos_id, call_data):
        """
        Remove liquidity from lp
        """
        tx = self._bank.execute(
            pos_id,
            self._spell,
            self._spell.removeLiquidityWERC20.encode_input(
                config["alpha-homora"]["pools"][self._lp_pair]["token0"],  
                config["alpha-homora"]["pools"][self._lp_pair]["token1"], 
                call_data,
            ),
            {'from': self._account}
        )
        return tx

    ##########################################################################
    def harvest_rewards(self, pos_id):
        """
        Harvest Rewards
        """
        wstaking = config["alpha-homora"]["pools"][self._lp_pair]["staking"]
        tx = self._bank.execute(
                pos_id,
                self._spell,
                self._spell.harvestWStakingRewards.encode_input(wstaking
                ),
            {'from': self._account}
        )
        return tx
