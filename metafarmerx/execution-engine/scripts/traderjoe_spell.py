import json
from web3 import Web3
from brownie import accounts, config, Contract
from .utils import load_abi, get_account


def add_liquidity(pos_id, call_data):
    account = get_account()
    bank = Contract.from_abi("HomoraBank", config["alpha-homora"]["HomoraBank"], load_abi(config["alpha-homora"]["HomoraBankABI"]))
    spell = Contract.from_abi("TraderJoeSpellV1", config["alpha-homora"]["pools"]["USDC.e/AVAX"]["spell"], load_abi(config["alpha-homora"]["pools"]["USDC.e/AVAX"]["spellAbi"]))
    tx = bank.execute(
        pos_id,
        spell,
        spell.addLiquidityWERC20.encode_input(
            config["alpha-homora"]["pools"]["USDC.e/AVAX"]["token0"],  # token 0
            config["alpha-homora"]["pools"]["USDC.e/AVAX"]["token1"],  # token 1
            call_data,  
        ),
        {'from': account}
    )
    return tx


def remove_liquidity(pos_id, call_data):
    account = get_account()
    bank = Contract.from_abi("HomoraBank", config["alpha-homora"]["HomoraBank"], load_abi(config["alpha-homora"]["HomoraBankABI"]))
    spell = Contract.from_abi("TraderJoeSpellV1", config["alpha-homora"]["pools"]["USDC.e/AVAX"]["spell"], load_abi(config["alpha-homora"]["pools"]["USDC.e/AVAX"]["spellAbi"]))
    tx = bank.execute(
        pos_id,
        spell,
        spell.removeLiquidityWERC20.encode_input(
            config["alpha-homora"]["pools"]["USDC.e/AVAX"]["token0"],  # token 0
            config["alpha-homora"]["pools"]["USDC.e/AVAX"]["token1"],  # token 1
            call_data,
        ),
        {'from': account}
    )
    return tx


def harvest_rewards(pos_id):
    account = get_account()
    bank = Contract.from_abi("HomoraBank", config["alpha-homora"]["HomoraBank"], load_abi(config["alpha-homora"]["HomoraBankABI"]))
    spell = Contract.from_abi("TraderJoeSpellV1", config["alpha-homora"]["pools"]["USDC.e/AVAX"]["spell"], load_abi(config["alpha-homora"]["pools"]["USDC.e/AVAX"]["spellAbi"]))
    wstaking = config["alpha-homora"]["pools"]["USDC.e/AVAX"]["staking"]
    tx = bank.execute(
        pos_id,
        spell,
        spell.harvestWStakingRewards.encode_input(wstaking),
        {'from': account}
    )
    return tx
