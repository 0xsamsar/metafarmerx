# ------------- SCRIPT ------------- #
#!/bin/bash
source .env
brownie networks modify avax-main host=$AVAX_RPC_URL
# ------------- END ------------- #