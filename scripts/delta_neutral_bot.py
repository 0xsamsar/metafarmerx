'''
        __  ___     __        ______                              _  __
       /  |/  /__  / /_____ _/ ____/___ __________ ___  ___  ____| |/ /
      / /|_/ / _ \/ __/ __ `/ /_  / __ `/ ___/ __ `__ \/ _ \/ ___/   / 
     / /  / /  __/ /_/ /_/ / __/ / /_/ / /  / / / / / /  __/ /  /   |  
    /_/  /_/\___/\__/\__,_/_/    \__,_/_/  /_/ /_/ /_/\___/_/  /_/|_|  

'''

import sys

sys.path.append("./metafarmerx")

from multiprocessing import Process

from brownie import network
from cli.selections import user_selections
from core.market_feed import MarketFeed
from core.strategy import Strategy

from .config_manager import get_account
from .position_manager import open_position


def main():
    # Load Trading Bot Account
    account = get_account()

    # Load User Selected Strategy Configs
    lp_pair, leverage, supply_amt, update_frequency = user_selections()

    # Create Delta Neutral Position
    pos_id, stable_borrow_amt, risky_borrow_amt = open_position(lp_pair, leverage, supply_amt, account)
    
    # Instantiate Market Feed Handler
    market_feed = MarketFeed(pos_id, lp_pair, update_frequency)
    market_feed_executor = Process(target=market_feed.run)
    market_feed_executor.start()

    # Instantiate Strategy Handler
    strategy = Strategy(pos_id, 
                        lp_pair, 
                        leverage, 
                        supply_amt, 
                        stable_borrow_amt,
                        risky_borrow_amt)

    strategy_executor = Process(target=strategy.poll)
    strategy_executor.start()

    # Wait for Subprocess Termination
    strategy_executor.join()
    market_feed_executor.join()


if __name__ == "__main__":
    main()
