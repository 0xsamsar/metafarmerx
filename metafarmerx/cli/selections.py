from pick import pick
from .console import INIT_MSG

def user_selections():
    """
    User inputs srategy configs
    """
    title = INIT_MSG + "[MetaFarmerX] Select Yield Farm (Alpha Homora V2 AVAX): "
    options = ['USDC.e/AVAX', 'AVAX/USDT.e (soon)', 'AVAX/DAI.e (soon)']
    selected = pick(options, title, multiselect=False, min_selection_count=1)
    lp_pair = selected[0]
 
    title = INIT_MSG + "[MetaFarmerX] Select Leverage Multiple [2x|3x]: "
    options = [2.0, 3.0]
    selected = pick(options, title, multiselect=False, min_selection_count=1)
    leverage = selected[0]

    title = INIT_MSG + "[MetaFarmerX] Select Position Supply $Amount [USDC.e|USDT.e|DAI.e]: "
    options = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
    selected = pick(options, title, multiselect=False, min_selection_count=1)
    supply_amt = selected[0]

    title = INIT_MSG + "[MetaFarmerX] Select Update Frequency (seconds): "
    options = [1, 15, 30, 60, 900, 1800, 3600]
    selected = pick(options, title, multiselect=False, min_selection_count=1)
    update_frequency = selected[0]

    return lp_pair, leverage, supply_amt, update_frequency