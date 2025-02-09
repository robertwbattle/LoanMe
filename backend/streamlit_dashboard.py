import streamlit as st
import sqlite3
import pandas as pd

# Function to fetch data from the database
def fetch_data(query):
    conn = sqlite3.connect('loan_platform.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Streamlit app
st.title("LoanMe Dashboard")

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

# Layout adjustments
st.sidebar.header("LoanMe Dashboard")
st.sidebar.write("Use the sidebar to navigate through different sections of the dashboard.")

st.sidebar.subheader("Users Data")
st.sidebar.dataframe(users_df)

st.sidebar.subheader("Posts Data")
st.sidebar.dataframe(posts_df)

st.sidebar.subheader("Transactions Data")
st.sidebar.dataframe(transactions_df)

st.sidebar.subheader("Payments Data")
st.sidebar.dataframe(payments_df)

st.sidebar.subheader("Summary")
st.sidebar.write(f"Total Trading Volume: ${total_volume:.2f}")
st.sidebar.write(f"Average Loan Amount: ${average_loan:.2f}")
st.sidebar.write(f"Number of Users: {num_users}")
st.sidebar.write(f"Number of Transactions: {num_transactions}")
