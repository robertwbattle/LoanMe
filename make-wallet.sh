#!/bin/bash

# Set your Tatum API key
TATUM_API_KEY=""

# Generate Solana wallet
response=$(curl --location --request GET 'https://api-eu1.tatum.io/v3/solana/wallet' \
--header "x-api-key: $TATUM_API_KEY")

# Extract wallet information
address=$(echo $response | jq -r '.address')
private_key=$(echo $response | jq -r '.privateKey')

# Print wallet information
echo "Solana Wallet Generated:"
echo "Address: $address"
echo "Private Key: $private_key"

# Save wallet information to a file
echo "Address: $address" > solana_wallet.txt
echo "Private Key: $private_key" >> solana_wallet.txt

echo "Wallet information saved to solana_wallet.txt"
