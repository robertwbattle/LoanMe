import random
import sqlite3
from datetime import datetime, timedelta
import logging
from db import get_db_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_solana_address():
    # Simulated Solana address generation (44 characters)
    chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    return ''.join(random.choice(chars) for _ in range(44))

def insert_user():
    email = f'user_{random.randint(1000, 9999)}@test.com'
    password_hash = f'hash_{random.randint(1000, 9999)}'
    solana_address = generate_solana_address()
    solana_private_key = f'private_key_{random.randint(1000, 9999)}'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Users (email, password_hash, solana_address, solana_private_key)
        VALUES (?, ?, ?, ?)''', (email, password_hash, solana_address, solana_private_key))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id, solana_address

def create_loan_posting():
    # Create a user first to get both ID and wallet
    user_id, wallet_address = insert_user()
    
    loan_amount = round(random.uniform(0.1, 10.0), 2)
    interest_rate = round(random.uniform(1, 15), 2)
    
    # Randomly decide if this is a lender or borrower post
    is_lender = random.choice([True, False])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO Posts (
            lender_wallet,
            borrower_wallet,
            loan_amount,
            interest_rate,
            status
        ) VALUES (?, ?, ?, ?, 'open')''', 
        (wallet_address if is_lender else None,
         None if is_lender else wallet_address,
         loan_amount,
         interest_rate))
    
    post_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    logger.info(f"Created {'lender' if is_lender else 'borrower'} post {post_id} with amount {loan_amount} SOL")
    return post_id

def fulfill_loan_posting():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Select an open post
    cursor.execute('''
        SELECT post_id, lender_wallet, borrower_wallet, loan_amount, interest_rate 
        FROM Posts 
        WHERE status = 'open' 
        AND (lender_wallet IS NOT NULL OR borrower_wallet IS NOT NULL)
        LIMIT 1''')
    
    post = cursor.fetchone()
    
    if post:
        post_id, lender_wallet, borrower_wallet, loan_amount, interest_rate = post
        
        # If post has lender, create borrower. If post has borrower, create lender
        _, new_wallet = insert_user()
        
        if lender_wallet:
            borrower_wallet = new_wallet
        else:
            lender_wallet = new_wallet
            
        # Update post with the new wallet and mark as funded
        cursor.execute('''
            UPDATE Posts 
            SET lender_wallet = ?, 
                borrower_wallet = ?,
                status = 'funded' 
            WHERE post_id = ?''', 
            (lender_wallet, borrower_wallet, post_id))
        
        logger.info(f"Fulfilled post {post_id} between {lender_wallet} and {borrower_wallet}")
        
        conn.commit()
    else:
        logger.info("No open posts found to fulfill")
    
    conn.close()

def run_load_test(num_posts=10, num_fulfillments=5):
    logger.info(f"Starting load test with {num_posts} posts and {num_fulfillments} fulfillments")
    
    # Create posts
    for _ in range(num_posts):
        create_loan_posting()
    
    # Fulfill some posts
    for _ in range(num_fulfillments):
        fulfill_loan_posting()
    
    logger.info("Load test completed")

if __name__ == "__main__":
    run_load_test()
