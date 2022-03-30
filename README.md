# MetaFarmerX
**NOTE:** Development of MetaFarmerX will be taken to a private repo as this V1 POC will lead to the development of a robust farming system with proprietary delta neutral farming strategies. You can reach out to me on Twitter for further inquiry! [@0xSamsar](https://twitter.com/0xSamsar)

## Introduction
MetaFarmerX is a distributed yield-farming framework that can be used to to simplify building and deploying automated yield farming strategies while allowing for modularity in the lower-level communication protocol. This system can be used for data aggregation (on-chain & off-chain), trade execution, and strategy & portfolio management. The purpose of this repo is to provide a starting point for creating delta neutral farming bots. Rigorous failover policies, monitoring systems, and testing & validation frameworks are needed to build a production ready system. 

## Setup
- Install python libraries
- Set & source environment variables
- Implement ```AutoHedger``` class
- Adapt MarketFeed to publish data formatted for your needs
- Token Approvals ```brownie run scripts/config_manager.py```
- Run Trading Bot ```brownie run scripts/delta_neutral_bot.py```

## Integarations
- [x] Alpha Homora V2 (AVAX)

