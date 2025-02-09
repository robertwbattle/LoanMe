import sqlite3
import random
import string
import time
import requests
import json
from datetime import datetime, timedelta

# Tatum API key
TATUM_API_KEY = "t-67a7f0385e8016861a9fcd27-60fd4bd6921348ecb3ff2d79"

# Database connection
def get_db_connection():
    return sqlite3.connect('loan_platform.db')

# Generate Solana wallet using Tatum API
def generate_solana_wallet():
    url = 'https://api-eu1.tatum.io/v3/solana/wallet'
    headers = {"x-api-key": TATUM_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        wallet_info = response.json()
        address = wallet_info.get('address')
        private_key = wallet_info.get('privateKey')

        # Save wallet information to a file
        with open('solana_wallet.txt', 'a') as f:
            f.write(f"Address: {address}\n")
            f.write(f"Private Key: {private_key}\n")

        return address, private_key
    else:
        print("Error generating Solana wallet:", response.text)
        return None, None

# Generate random user data
def generate_user():
    email = ''.join(random.choices(string.ascii_lowercase, k=8)) + '@example.com'
    password_hash = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    solana_address, solana_private_key = generate_solana_wallet()
    return (password_hash, email, solana_address, solana_private_key)

# Insert user into database
def insert_user():
    user = generate_user()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Users (password_hash, email, solana_address, solana_private_key)
        VALUES (?, ?, ?, ?)''', user)
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

# Generate loan posting
def create_loan_posting(user_id):
    post_type = random.choice(['borrow', 'lend'])
    loan_amount = round(random.uniform(0.1, 0.3))
    interest_rate = round(random.uniform(1, 15), 2)
    payment_schedule_id = random.randint(1, 3)  # Assuming some schedules exist
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Posts (user_id, post_type, loan_amount, interest_rate, payment_schedule_id)
        VALUES (?, ?, ?, ?, ?)''', (user_id, post_type, loan_amount, interest_rate, payment_schedule_id))
    conn.commit()
    conn.close()

# Fulfill a loan posting
def fulfill_loan_posting():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Select an open post
    cursor.execute('SELECT post_id, user_id, loan_amount, interest_rate, payment_schedule_id FROM Posts WHERE status = "open" LIMIT 1')
    post = cursor.fetchone()
    
    if post:
        post_id, borrower_id, loan_amount, interest_rate, payment_schedule_id = post

        # Create lender
        lender_id = insert_user()

        # Insert transaction
        cursor.execute('''
            INSERT INTO Transactions (lender_id, borrower_id, post_id, loan_amount, interest_rate, payment_schedule_id, status)
            VALUES (?, ?, ?, ?, ?, ?, 'active')''', (lender_id, borrower_id, post_id, loan_amount, interest_rate, payment_schedule_id))

        # Update post status
        cursor.execute('UPDATE Posts SET status = "funded" WHERE post_id = ?', (post_id,))
        
        conn.commit()
    conn.close()

# Continuous generation of users, loan postings, and fulfillment
def simulate_activity():
    for i in range(200):
        user_id = insert_user()
        create_loan_posting(user_id)
        fulfill_loan_posting()
        print(f"User {user_id} created, posting made, and transactions processed.")
        time.sleep(5)  # Timer set to 5 seconds for demonstration

if __name__ == '__main__':
    simulate_activity()
