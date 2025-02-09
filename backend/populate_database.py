import sqlite3
from datetime import datetime, timedelta
import random

# Connect to the SQLite database
conn = sqlite3.connect('loan_platform.db')
cursor = conn.cursor()

# Insert sample users
users = [
    ('alice', 'hashed_password1', 'alice@example.com', 750),
    ('bob', 'hashed_password2', 'bob@example.com', 680),
    ('charlie', 'hashed_password3', 'charlie@example.com', 720),
    ('dave', 'hashed_password4', 'dave@example.com', 690),
    ('eve', 'hashed_password5', 'eve@example.com', 710),
    ('frank', 'hashed_password6', 'frank@example.com', 730),
    ('grace', 'hashed_password7', 'grace@example.com', 740),
    ('heidi', 'hashed_password8', 'heidi@example.com', 760),
    ('ivan', 'hashed_password9', 'ivan@example.com', 680),
    ('judy', 'hashed_password10', 'judy@example.com', 700)
]

for username, password_hash, email, score in users:
    cursor.execute("""
        INSERT OR IGNORE INTO Users (username, password_hash, email, score)
        VALUES (?, ?, ?, ?)
    """, (username, password_hash, email, score))

# Insert sample payment schedules
schedules = [
    ('weekly', 6),
    ('bi-weekly', 12),
    ('monthly', 24)
]

for frequency, duration in schedules:
    cursor.execute("""
        INSERT OR IGNORE INTO PaymentSchedules (frequency, duration_in_months)
        VALUES (?, ?)
    """, (frequency, duration))

# Retrieve user and schedule IDs
cursor.execute("SELECT user_id FROM Users")
user_ids = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT schedule_id FROM PaymentSchedules")
schedule_ids = [row[0] for row in cursor.fetchall()]

# Insert sample posts
for _ in range(50):  # 50 sample posts
    user_id = random.choice(user_ids)
    post_type = random.choice(['borrow', 'lend'])
    loan_amount = random.randint(1000, 10000)
    interest_rate = round(random.uniform(3.5, 8.0), 2)
    payment_schedule_id = random.choice(schedule_ids)

    cursor.execute("""
        INSERT INTO Posts (user_id, post_type, loan_amount, interest_rate, payment_schedule_id, status)
        VALUES (?, ?, ?, ?, ?, 'open')
    """, (user_id, post_type, loan_amount, interest_rate, payment_schedule_id))

# Insert sample transactions
cursor.execute("SELECT post_id FROM Posts")
post_ids = [row[0] for row in cursor.fetchall()]

for _ in range(30):  # 30 sample transactions
    lender_id, borrower_id = random.sample(user_ids, 2)
    post_id = random.choice(post_ids)
    loan_amount = random.randint(1000, 10000)
    interest_rate = round(random.uniform(3.5, 8.0), 2)
    payment_schedule_id = random.choice(schedule_ids)
    blockchain_tx_id = f'solana_tx_{random.randint(1000, 9999)}'

    cursor.execute("""
        INSERT INTO Transactions (lender_id, borrower_id, post_id, loan_amount, interest_rate, payment_schedule_id, blockchain_tx_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
    """, (lender_id, borrower_id, post_id, loan_amount, interest_rate, payment_schedule_id, blockchain_tx_id))

# Insert sample payments
cursor.execute("SELECT transaction_id FROM Transactions")
transaction_ids = [row[0] for row in cursor.fetchall()]

today = datetime.now()

for txn_id in transaction_ids:
    for i in range(6):  # 6 payments per transaction
        due_date = today + timedelta(days=30 * (i + 1))
        amount_due = random.randint(500, 2000)

        cursor.execute("""
            INSERT INTO Payments (transaction_id, due_date, amount_due, amount_paid, payment_status)
            VALUES (?, ?, ?, ?, 'due')
        """, (txn_id, due_date.date(), amount_due, 0))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database populated with extensive sample data successfully!")
