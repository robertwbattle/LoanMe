import sqlite3

# Connect to the database
conn = sqlite3.connect('loan_platform.db')
cursor = conn.cursor()

cursor.execute("INSERT OR REPLACE INTO Users (username, password_hash, email) VALUES (?, ?, ?)", 
               ('alice', 'hashed_password1', 'alice@example.com'))
cursor.execute("INSERT OR REPLACE INTO Users (username, password_hash, email) VALUES (?, ?, ?)", 
               ('bob', 'hashed_password2', 'bob@example.com'))

cursor.execute("INSERT OR REPLACE INTO PaymentSchedules (frequency, duration_in_months) VALUES (?, ?)", 
               ('monthly', 12))
cursor.execute("INSERT OR REPLACE INTO PaymentSchedules (frequency, duration_in_months) VALUES (?, ?)", 
               ('bi-weekly', 24))
cursor.execute("INSERT OR REPLACE INTO PaymentSchedules (frequency, duration_in_months) VALUES (?, ?)", 
               ('weekly', 6))

sample_posts = [
    {"user_id": alice_id, "post_type": "borrow", "loan_amount": 5000, "interest_rate": 5.2, "payment_schedule_id": monthly_schedule_id},
    {"user_id": bob_id, "post_type": "lend", "loan_amount": 7500, "interest_rate": 4.8, "payment_schedule_id": biweekly_schedule_id},
    {"user_id": alice_id, "post_type": "borrow", "loan_amount": 3000, "interest_rate": 6.1, "payment_schedule_id": weekly_schedule_id}
]

for post in sample_posts:
    cursor.execute("""
        INSERT INTO Posts (user_id, post_type, loan_amount, interest_rate, payment_schedule_id, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (post['user_id'], post['post_type'], post['loan_amount'], post['interest_rate'], post['payment_schedule_id'], 'open'))

# Commit after inserting users and schedules to ensure data persistence
conn.commit()

# Get user IDs
cursor.execute("SELECT user_id FROM Users WHERE username = 'alice'")
alice = cursor.fetchone()
cursor.execute("SELECT user_id FROM Users WHERE username = 'bob'")
bob = cursor.fetchone()

# Get payment schedule IDs
cursor.execute("SELECT schedule_id FROM PaymentSchedules WHERE frequency = 'monthly'")
monthly_schedule = cursor.fetchone()
cursor.execute("SELECT schedule_id FROM PaymentSchedules WHERE frequency = 'Bi-Weekly'")
biweekly_schedule = cursor.fetchone()
cursor.execute("SELECT schedule_id FROM PaymentSchedules WHERE frequency = 'Weekly'")
weekly_schedule = cursor.fetchone()

# Check if the data exists
if not all([alice, bob, monthly_schedule, biweekly_schedule, weekly_schedule]):
    raise ValueError("Missing user or payment schedule data!")

# Map IDs for easier reference
alice_id = alice[0]
bob_id = bob[0]
monthly_schedule_id = monthly_schedule[0]
biweekly_schedule_id = biweekly_schedule[0]
weekly_schedule_id = weekly_schedule[0]


# Commit changes and close the connection
conn.commit()
conn.close()

print("Sample loan postings inserted successfully!")
