#!/bin/bash

# Check if a wallet address is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <wallet_address>"
    exit 1
fi

# Store the wallet address
WALLET_ADDRESS=$1

# Get the balance using Solana CLI
BALANCE=$(solana balance $WALLET_ADDRESS --url https://api.devnet.solana.com)

# Check if the balance command was successful
if [ $? -eq 0 ]; then
    echo "Balance for wallet $WALLET_ADDRESS:"
    echo "$BALANCE"
else
    echo "Error: Failed to retrieve balance for wallet $WALLET_ADDRESS"
    exit 1
fi
