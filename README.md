# MetaFarmerX
Robust Yield Farming Engine

## Introduction
MetaFarmerX is a distributed yield-farming system (inspired by MetaTrader) that can be used to to simplify building and deploying automated yield farming strategies. This system can be used for acquiring market data (on-chain & off-chain), trade execution, and strategy & portfolio managemnt.

## Libraries
- Brownie
- ZeroMQ
- Web3

## Design Pillars
- Scalability
- Reliability
- Availability
- Modularity

## Strategy 1: Delta Neutral Farming
To describe the strategy, let’s use the USDC.e/AVAX farm on Alpha-Homora V2 (avalanche) as an example. Assume we have $10,000 USDC which we plan to yield farm with. Since Alpha Homora allows for loans on both sides of an LP pair, we can create our delta neutral position by just supplying USDC and borrowing against it.

### AVAX Long Exposure 
We deposit $2,500 USDC and borrow $5,000 USDC to achieve 3x leverage. The platform automatically balances the position to 50-50 since equal amounts need to be added to the pool. Our AVAX long exposure is $7,500 - $3,750 = $3,750.
### AVAX Short Exposure 
We deposit $7,500 USDC and borrow $15,000 equivalent of AVAX to achieve 3x leverage. The platform automatically balances the position to 50-50 since equal amounts need to be added to the pool.  Our AVAX short exposure is $15,000 - $11,250 = $3,750.

In essence, when one position is out of the money (OTM), the other will be in the money (ITM). Therefore, we can rebalance the positions by moving the collateral from the ITM position and add to the OTM position.


