-- Users Table
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    score REAL DEFAULT 0, -- Custom score to assess loan repayment ability
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posts Table (for both Borrow and Lend posts)
CREATE TABLE Posts (
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
CREATE TABLE PaymentSchedules (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    frequency TEXT CHECK(frequency IN ('weekly', 'bi-weekly', 'monthly')) NOT NULL,
    duration_in_months INTEGER NOT NULL
);

-- Transactions Table
CREATE TABLE Transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lender_id INTEGER NOT NULL,
    borrower_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    loan_amount REAL NOT NULL,
    interest_rate REAL NOT NULL,
    payment_schedule_id INTEGER NOT NULL,
    blockchain_tx_id TEXT, -- Reference to Solana blockchain transaction ID
    status TEXT CHECK(status IN ('pending', 'active', 'completed', 'defaulted')) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lender_id) REFERENCES Users(user_id),
    FOREIGN KEY (borrower_id) REFERENCES Users(user_id),
    FOREIGN KEY (post_id) REFERENCES Posts(post_id),
    FOREIGN KEY (payment_schedule_id) REFERENCES PaymentSchedules(schedule_id)
);

-- Payments Table (to track individual payment instances)
CREATE TABLE Payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    due_date DATE NOT NULL,
    amount_due REAL NOT NULL,
    amount_paid REAL DEFAULT 0,
    payment_status TEXT CHECK(payment_status IN ('due', 'paid', 'late')) DEFAULT 'due',
    blockchain_payment_id TEXT, -- Solana payment reference
    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
);
