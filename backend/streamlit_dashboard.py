import streamlit as st
import sqlite3
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import json
import ast
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Function definitions first
def convert_private_key_to_array(private_key_str):
    """Convert string representation of private key array back to array of integers"""
    try:
        return ast.literal_eval(private_key_str)
    except:
        st.error("Error converting private key string to array")
        return None

def get_user_stats():
    """Get simplified user statistics from database"""
    conn = sqlite3.connect('loan_platform.db')
    
    # Loan amounts by user
    loan_amounts = pd.read_sql_query("""
        SELECT 
            u.email,
            COUNT(p.post_id) as total_loans,
            SUM(p.loan_amount) as total_amount,
            AVG(p.interest_rate) as avg_interest
        FROM Users u
        LEFT JOIN Posts p ON u.user_id = p.user_id
        GROUP BY u.email
    """, conn)
    
    # Activity over time (last 30 days)
    activity = pd.read_sql_query("""
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as num_posts
        FROM Posts
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        LIMIT 30
    """, conn)
    
    # Post status distribution
    status_dist = pd.read_sql_query("""
        SELECT 
            status,
            COUNT(*) as count
        FROM Posts
        GROUP BY status
    """, conn)
    
    conn.close()
    return loan_amounts, activity, status_dist

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
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {'success': False, 'error': 'Invalid JSON response'}

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

# Function to get program info
def get_program_info(program_id):
    url = f'http://127.0.0.1:5000/api/program/{program_id}'
    response = requests.get(url)
    try:
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {'success': False, 'error': f'HTTP error occurred: {http_err}'}
    except requests.exceptions.JSONDecodeError:
        return {'success': False, 'error': 'Invalid JSON response'}
    except Exception as err:
        return {'success': False, 'error': f'Other error occurred: {err}'}

# Streamlit app
st.title("Loan Platform Dashboard")

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
        program_id = deploy_result['programId']
    else:
        st.error(f"Contract deployment failed: {deploy_result['error']}")

# Program ID
st.header("Program ID")
program_id = os.getenv("PROGRAM_ID")
if program_id:
    program_info = get_program_info(program_id)
    if program_info['success']:
        st.write(f"Program ID: {program_id}")
        st.write(f"Exists: {program_info['exists']}")
        st.write(f"Executable: {program_info['executable']}")
        st.write(f"Lamports: {program_info['lamports']}")
        st.write(f"Owner: {program_info['owner']}")
        st.write(f"Data Length: {program_info['data_len']}")
    else:
        st.error(f"Failed to fetch program info: {program_info['error']}")
else:
    st.error("Program ID not found in environment variables")

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

# Sidebar
with st.sidebar:
    st.header("Loan Actions")
    action = st.selectbox(
        "Select Action",
        ["Analytics", "Check Balance", "Create Loan", "Transfer SOL"]
    )

# Main content
if action == "Analytics":
    st.header("Analytics Dashboard")
    
    try:
        loan_amounts, activity, status_dist = get_user_stats()
        
        # Key metrics at the top
        st.header("Key Metrics")
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

        with metrics_col1:
            total_users = len(loan_amounts)
            st.metric("Total Users", total_users)

        with metrics_col2:
            total_loans = loan_amounts['total_loans'].sum()
            st.metric("Total Loans", total_loans)

        with metrics_col3:
            total_volume = loan_amounts['total_amount'].sum()
            st.metric("Total Volume (SOL)", f"{total_volume:.2f}")

        # Graphs
        col1, col2 = st.columns(2)

        with col1:
            # Loan status distribution
            st.subheader("Loan Status Distribution")
            fig = px.pie(status_dist,
                        values='count',
                        names='status',
                        title='Current Loan Status')
            st.plotly_chart(fig)

            # User activity
            st.subheader("User Activity")
            fig = px.bar(loan_amounts,
                        x='email',
                        y='total_loans',
                        title='Loans per User')
            st.plotly_chart(fig)

        with col2:
            # Activity over time
            st.subheader("Platform Activity")
            fig = px.line(activity,
                         x='date',
                         y='num_posts',
                         title='Daily Post Activity')
            st.plotly_chart(fig)

            # Average interest rates
            st.subheader("Interest Rates by User")
            fig = px.scatter(loan_amounts,
                           x='total_amount',
                           y='avg_interest',
                           hover_data=['email'],
                           title='Average Interest Rates vs Total Amount')
            st.plotly_chart(fig)

        # Show raw data in expandable section
        with st.expander("View Raw Data"):
            st.subheader("Loan Data by User")
            st.dataframe(loan_amounts)
            
            st.subheader("Status Distribution")
            st.dataframe(status_dist)
            
            st.subheader("Activity Over Time")
            st.dataframe(activity)
            
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
        st.error("Detailed error info for debugging:")
        st.exception(e)

elif action == "Check Balance":
    st.header("Check Wallet Balance")
    wallet_address = st.text_input("Enter Wallet Address")
    
    if st.button("Check Balance"):
        try:
            response = requests.get(f"http://127.0.0.1:5000/api/solana/balance/{wallet_address}")
            if response.ok:
                data = response.json()
                if data['success']:
                    st.success(f"Balance: {data['balance_sol']} SOL")
                else:
                    st.error(f"Error: {data.get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"Error checking balance: {str(e)}")

elif action == "Create Loan":
    st.header("Create New Loan")
    loan_amount = st.number_input("Loan Amount (SOL)", min_value=0.1, step=0.1)
    interest_rate = st.number_input("Interest Rate (%)", min_value=0.1, step=0.1)
    
    role = st.radio("I am a:", ("Lender", "Borrower"))
    wallet_address = st.text_input("Your Wallet Address")
    
    if st.button("Create Loan"):
        try:
            payload = {
                "loan_amount": loan_amount,
                "interest_rate": interest_rate,
                "lender_wallet": wallet_address if role == "Lender" else None,
                "borrower_wallet": wallet_address if role == "Borrower" else None
            }
            
            response = requests.post(
                "http://127.0.0.1:5000/api/loans",
                json=payload
            )
            
            if response.ok:
                data = response.json()
                if data['success']:
                    st.success(f"Loan post created! Post ID: {data['post_id']}")
                    st.json(data['details'])
                else:
                    st.error(f"Error: {data.get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"Error creating loan: {str(e)}")

elif action == "Transfer SOL":
    st.header("Transfer SOL")
    
    sender_public = st.text_input("From (Public Key)")
    recipient_public = st.text_input("To (Public Key)")
    amount = st.number_input("Amount (SOL)", min_value=0.000001, step=0.1)
    
    if st.button("Transfer"):
        if not (sender_public and recipient_public and amount):
            st.error("Please fill in all fields")
        else:
            try:
                conn = sqlite3.connect('loan_platform.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT solana_private_key 
                    FROM Users 
                    WHERE solana_address = ?
                ''', (sender_public,))
                
                result = cursor.fetchone()
                conn.close()
                
                if not result:
                    st.error("Sender's wallet not found in database")
                else:
                    private_key_str = result[0]
                    private_key_array = convert_private_key_to_array(private_key_str)
                    
                    if not private_key_array:
                        st.error("Invalid private key format")
                    else:
                        payload = {
                            "private_key": private_key_array,
                            "wallet_to": recipient_public,
                            "transfer_amount": amount
                        }
                        
                        response = requests.post(
                            "http://127.0.0.1:5000/api/solana/transfer",
                            json=payload
                        )
                        
                        if response.ok:
                            data = response.json()
                            if data['success']:
                                st.success("Transfer successful!")
                                st.json({
                                    "signature": data['signature'],
                                    "amount": data['amount'],
                                    "recipient": data['recipient']
                                })
                            else:
                                st.error(f"Error: {data.get('error', 'Unknown error')}")
                        else:
                            st.error("Failed to make transfer request")
                            
            except Exception as e:
                st.error(f"Error during transfer: {str(e)}")
