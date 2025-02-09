import streamlit as st
import sqlite3
import pandas as pd
import requests

# Function to fetch data from the database
def fetch_data(query):
    conn = sqlite3.connect('loan_platform.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to transfer SOL
def transfer_sol(destination, amount):
    url = 'http://127.0.0.1:5000/api/wallet/transfer'
    payload = {
        'destination': destination,
        'amount': amount
    }
    response = requests.post(url, json=payload)
    return response.json()

# Function to get wallet balance
def get_wallet_balance():
    url = 'http://127.0.0.1:5000/api/wallet/balance'
    response = requests.get(url)
    return response.json()

# Function to get wallet address
def get_wallet_address():
    url = 'http://127.0.0.1:5000/api/wallet/address'
    response = requests.get(url)
    return response.json()

# Function to deploy contract
def deploy_contract():
    url = 'http://127.0.0.1:5000/api/deploy'
    response = requests.post(url)
    return response.json()

# Streamlit app
st.title("LoanMe Dashboard")

# Wallet Address
st.header("Admin Wallet Address")
wallet_address = get_wallet_address()
if wallet_address['success']:
    st.write(f"Wallet Address: {wallet_address['address']}")
else:
    st.error(f"Failed to fetch wallet address: {wallet_address['error']}")

# Deploy Contract
st.header("Deploy Contract")
if st.button("Deploy Contract"):
    deploy_result = deploy_contract()
    if deploy_result['success']:
        st.success(f"Contract deployed successfully! Program ID: {deploy_result['programId']}")
    else:
        st.error(f"Contract deployment failed: {deploy_result['error']}")

# Users Data
st.header("Users Data")
users_query = "SELECT user_id, email, score, created_at, solana_address FROM Users"
users_df = fetch_data(users_query)
st.dataframe(users_df)

# Posts Data
st.header("Posts Data")
posts_query = "SELECT post_id, user_id, post_type, loan_amount, interest_rate, status, created_at FROM Posts"
posts_df = fetch_data(posts_query)
st.dataframe(posts_df)

# Transactions Data
st.header("Transactions Data")
transactions_query = "SELECT transaction_id, lender_id, borrower_id, post_id, loan_amount, interest_rate, status, created_at FROM Transactions"
transactions_df = fetch_data(transactions_query)
st.dataframe(transactions_df)

# Payments Data
st.header("Payments Data")
payments_query = "SELECT payment_id, transaction_id, due_date, amount_due, amount_paid, payment_status FROM Payments"
payments_df = fetch_data(payments_query)
st.dataframe(payments_df)

# Total Volume
st.header("Total Volume")
total_volume_query = "SELECT SUM(loan_amount) as total_volume FROM Transactions"
total_volume_df = fetch_data(total_volume_query)
total_volume = total_volume_df['total_volume'][0] if total_volume_df['total_volume'][0] is not None else 0
st.write(f"Total Trading Volume: ${total_volume:.2f}")

# Average Loan Amount
st.header("Average Loan Amount")
average_loan_query = "SELECT AVG(loan_amount) as average_loan FROM Transactions"
average_loan_df = fetch_data(average_loan_query)
average_loan = average_loan_df['average_loan'][0] if average_loan_df['average_loan'][0] is not None else 0
st.write(f"Average Loan Amount: ${average_loan:.2f}")

# Number of Users
st.header("Number of Users")
num_users_query = "SELECT COUNT(user_id) as num_users FROM Users"
num_users_df = fetch_data(num_users_query)
num_users = num_users_df['num_users'][0] if num_users_df['num_users'][0] is not None else 0
st.write(f"Number of Users: {num_users}")

# Number of Transactions
st.header("Number of Transactions")
num_transactions_query = "SELECT COUNT(transaction_id) as num_transactions FROM Transactions"
num_transactions_df = fetch_data(num_transactions_query)
num_transactions = num_transactions_df['num_transactions'][0] if num_transactions_df['num_transactions'][0] is not None else 0
st.write(f"Number of Transactions: {num_transactions}")

# Wallet Balance
st.header("Wallet Balance")
wallet_balance = get_wallet_balance()
if wallet_balance['success']:
    st.write(f"Wallet Balance: {wallet_balance['balance']} SOL")
else:
    st.error(f"Failed to fetch wallet balance: {wallet_balance['error']}")

# Transfer SOL
st.header("Transfer SOL")
destination = st.text_input("Destination Address")
amount = st.text_input("Amount (SOL)")
if st.button("Send SOL"):
    if destination and amount:
        result = transfer_sol(destination, amount)
        if result['success']:
            st.success(f"Transfer successful! Signature: {result['signature']}")
        else:
            st.error(f"Transfer failed: {result['error']}")
    else:
        st.error("Please enter both destination address and amount.")
