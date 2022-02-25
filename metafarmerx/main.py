import sys
import logging

from time import sleep
from  multiprocessing import Process

from brownie import accounts, config, Contract

sys.path.append("/home/fazel/consensys/concave/MetaFarmerX/")
sys.path.append("/home/fazel/consensys/concave/MetaFarmerX/metafarmerx")

from strategy.delta_neutral import DeltaNeutral
from messaging.mfx_publisher import MFXPublisher
from protocols.homora.alpha_homora_v2 import AlphaHomoraV2

def main():
    # initialize evm interaction configs
    try:
        account = accounts.load('admin')
    
    except:
        sys.exit('Failed to load account')

    # # initialize the market feeds
    publisher = MFXPublisher()
    market_feeds = Process(target=publisher.run)
    market_feeds.start()
    
    # # ensure the server doesn't get a request before init
    sleep(2)

    # initialize the strategy 
    subscriber = DeltaNeutral()
    strategy = Process(target=subscriber.poll)
    strategy.start()

    #TODO Implement builder/factory class for loading the executors 


    strategy.join()



if __name__ == "__main__":
    main()