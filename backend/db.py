import sqlite3
from datetime import datetime

def setup_database():
    # Connect to SQLite database
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()

    # Create tables
    cursor.executescript('''
    -- Users Table
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        score REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Posts Table
    CREATE TABLE IF NOT EXISTS Posts (
        post_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        post_type TEXT CHECK(post_type IN ('borrow', 'lend')) NOT NULL,
        loan_amount REAL NOT NULL,
        interest_rate REAL NOT NULL,
        payment_schedule_id INTEGER,
        status TEXT CHECK(status IN ('open', 'funded', 'closed')) DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (payment_schedule_id) REFERENCES PaymentSchedules(schedule_id)
    );

    -- Payment Schedules Table
    CREATE TABLE IF NOT EXISTS PaymentSchedules (
        schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        frequency TEXT CHECK(frequency IN ('weekly', 'bi-weekly', 'monthly')) NOT NULL,
        duration_in_months INTEGER NOT NULL
    );

    -- Transactions Table
    CREATE TABLE IF NOT EXISTS Transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        lender_id INTEGER NOT NULL,
        borrower_id INTEGER NOT NULL,
        post_id INTEGER NOT NULL,
        loan_amount REAL NOT NULL,
        interest_rate REAL NOT NULL,
        payment_schedule_id INTEGER NOT NULL,
        blockchain_tx_id TEXT,
        status TEXT CHECK(status IN ('pending', 'active', 'completed', 'defaulted')) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (lender_id) REFERENCES Users(user_id),
        FOREIGN KEY (borrower_id) REFERENCES Users(user_id),
        FOREIGN KEY (post_id) REFERENCES Posts(post_id),
        FOREIGN KEY (payment_schedule_id) REFERENCES PaymentSchedules(schedule_id)
    );

    -- Payments Table
    CREATE TABLE IF NOT EXISTS Payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id INTEGER NOT NULL,
        due_date DATE NOT NULL,
        amount_due REAL NOT NULL,
        amount_paid REAL DEFAULT 0,
        payment_status TEXT CHECK(payment_status IN ('due', 'paid', 'late')) DEFAULT 'due',
        blockchain_payment_id TEXT,
        FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
    );
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# # Call the setup function to create the database and tables
# setup_database()

# Basic functions for adding and changing each field

def add_user(username, password_hash, email, score=0):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Users (username, password_hash, email, score)
        VALUES (?, ?, ?, ?)
    ''', (username, password_hash, email, score))
    conn.commit()
    conn.close()

def update_user_score(user_id, new_score):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Users
        SET score = ?
        WHERE user_id = ?
    ''', (new_score, user_id))
    conn.commit()
    conn.close()

def add_post(user_id, post_type, loan_amount, interest_rate, payment_schedule_id=None):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Posts (user_id, post_type, loan_amount, interest_rate, payment_schedule_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, post_type, loan_amount, interest_rate, payment_schedule_id))
    conn.commit()
    conn.close()

def update_post_status(post_id, new_status):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Posts
        SET status = ?
        WHERE post_id = ?
    ''', (new_status, post_id))
    conn.commit()
    conn.close()

def add_payment_schedule(frequency, duration_in_months):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO PaymentSchedules (frequency, duration_in_months)
        VALUES (?, ?)
    ''', (frequency, duration_in_months))
    conn.commit()
    conn.close()

def add_transaction(lender_id, borrower_id, post_id, loan_amount, interest_rate, payment_schedule_id, blockchain_tx_id=None):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Transactions (lender_id, borrower_id, post_id, loan_amount, interest_rate, payment_schedule_id, blockchain_tx_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (lender_id, borrower_id, post_id, loan_amount, interest_rate, payment_schedule_id, blockchain_tx_id))
    conn.commit()
    conn.close()

def update_transaction_status(transaction_id, new_status):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Transactions
        SET status = ?
        WHERE transaction_id = ?
    ''', (new_status, transaction_id))
    conn.commit()
    conn.close()

def add_payment(transaction_id, due_date, amount_due, amount_paid=0, payment_status='due', blockchain_payment_id=None):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Payments (transaction_id, due_date, amount_due, amount_paid, payment_status, blockchain_payment_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (transaction_id, due_date, amount_due, amount_paid, payment_status, blockchain_payment_id))
    conn.commit()
    conn.close()

def update_payment_status(payment_id, new_status):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Payments
        SET payment_status = ?
        WHERE payment_id = ?
    ''', (new_status, payment_id))
    conn.commit()
    conn.close()

# Getter functions for each data type

def get_user(user_id):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Users WHERE user_id = ?
    ''', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_post(post_id):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Posts WHERE post_id = ?
    ''', (post_id,))
    post = cursor.fetchone()
    conn.close()
    return post

def get_payment_schedule(schedule_id):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM PaymentSchedules WHERE schedule_id = ?
    ''', (schedule_id,))
    schedule = cursor.fetchone()
    conn.close()
    return schedule

def get_transaction(transaction_id):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Transactions WHERE transaction_id = ?
    ''', (transaction_id,))
    transaction = cursor.fetchone()
    conn.close()
    return transaction

def get_payment(payment_id):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Payments WHERE payment_id = ?
    ''', (payment_id,))
    payment = cursor.fetchone()
    conn.close()
    return payment
