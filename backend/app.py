from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_post, get_user, get_payment_schedule, get_transaction, get_payment
from db import create_post, create_user, create_transaction, create_payment
import sqlite3
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.publickey import PublicKey
from anchorpy import Provider, Program, Wallet
import json
import os
from dotenv import load_dotenv
import time

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# check if there already exist a wallet for the User
def check_existing_wallet(user_id):
    try:
        conn = sqlite3.connect('loan_platform.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT solana_address, solana_private_key 
            FROM Users 
            WHERE user_id = ?
        """, (user_id,))
        
        wallet = cursor.fetchone()
        conn.close()
        
        if wallet and wallet[0] and wallet[1]:  # Check if both address and private key exist
            return True, {
                "solana_address": wallet[0],
                "solana_private_key": wallet[1]
            }
        return False, None
        
    except Exception as e:
        return None, str(e)

# Solana setup
async def get_solana_client():
    client = AsyncClient("https://api.devnet.solana.com")
    provider = Provider(
        client,
        Wallet(Keypair.from_secret_key(json.loads(os.getenv("WALLET_PRIVATE_KEY")))),
    )
    
    # Load IDL from anchor/target/idl/sol_backend.json
    with open('../anchor/target/idl/sol_backend.json', 'r') as f:
        idl = json.load(f)
    
    program_id = PublicKey(os.getenv("PROGRAM_ID"))
    program = Program(idl, program_id, provider)
    return client, program

# ✅ Existing API - Get a Single Loan Post
@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Posts WHERE post_id = ?", (post_id,))
    post = cursor.fetchone()
    conn.close()

    if post:
        return jsonify({
            "post_id": post[0],
            "account_name": post[1],
            "loan_amount": post[2],
            "interest_rate": post[3],
            "payment_schedule": post[4],
            "description": "Detailed information about this loan post."
        })
    return jsonify({"error": "Post not found"}), 404


# ✅ New API - Get All Loan Posts
@app.route('/api/posts', methods=['GET'])
def get_posts():
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()

    # Simplified Query (No Joins)
    cursor.execute("SELECT post_id, loan_amount, interest_rate, status FROM Posts WHERE status = 'open'")
    posts = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "id": post[0],
            "loan_amount": post[1],
            "interest_rate": post[2],
            "status": post[3]
        }
        for post in posts
    ])


@app.route('/api/activity', methods=['GET'])
def get_activity():
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()

    # Example: Fetch user's posts as activity
    cursor.execute("""
        SELECT p.post_type, p.loan_amount, p.status, u.username
        FROM Posts p
        JOIN Users u ON p.user_id = u.user_id
        ORDER BY p.created_at DESC
    """)
    activities = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "type": post[0],                # borrow/lend
            "details": f"Loan of ${post[1]} ({post[2]}) by {post[3]}"
        }
        for post in activities
    ])


# ✅ Generate a test solana wallet given userID and Store it in the DB
@app.route('/api/generate-wallet/<int:user_id>', methods=['POST'])
def generate_wallet(user_id):
    try:
        # First check if wallet exists
        wallet_exists, existing_wallet = check_existing_wallet(user_id)
        
        if wallet_exists:
            return jsonify({
                "success": True,
                "message": "Wallet already exists for this user",
                "wallet": {
                    "address": existing_wallet['solana_address'],
                    "private_key": existing_wallet['solana_private_key']
                },
                "user_id": user_id
            })
            
        # If no wallet exists, proceed with generation
        TATUM_API_KEY = os.getenv('TATUM_API_KEY')
        TATUM_API_URL = os.getenv('TATUM_API_URL')
        
        headers = {
            "x-api-key": TATUM_API_KEY
        }
        
        response = requests.get(TATUM_API_URL, headers=headers)
        
        if response.status_code == 200:
            wallet_data = response.json()
            
            # Update user record with wallet information
            conn = sqlite3.connect('loan_platform.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE Users 
                SET solana_address = ?, solana_private_key = ?
                WHERE user_id = ?
            """, (wallet_data['address'], wallet_data['privateKey'], user_id))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                "success": True,
                "message": "New wallet generated successfully",
                "wallet": {
                    "address": wallet_data['address'],
                    "private_key": wallet_data['privateKey']
                },
                "user_id": user_id
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to generate wallet",
                "status_code": response.status_code
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



@app.route('/api/account', methods=['POST', 'OPTIONS'])
def create_account():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    elif request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        # solana_address = data.get('solana_address')
        # solana_private_key = data.get('solana_private_key')
        # Add logic to create account
        create_user(password, email, None, None)
        return jsonify({"success": True, "message": "Account created successfully"})

def _build_cors_preflight_response():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

# Create loan endpoint
@app.route('/api/loans', methods=['POST'])
async def create_loan():
    try:
        data = request.json
        client, program = await get_solana_client()
        
        borrower = PublicKey(data['borrowerPublicKey'])
        loan_amount = data['loanAmount']
        apy = data['apy']
        duration = data['duration']
        timestamp = int(time.time() * 1000)

        tx = await program.rpc["create_loan"](
            loan_amount,
            apy,
            duration,
            timestamp,
            accounts={
                'lender': program.provider.wallet.public_key,
                'borrower': borrower,
            }
        )

        return jsonify({
            'success': True,
            'transaction': str(tx),
            'timestamp': timestamp
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Make payment endpoint
@app.route('/api/loans/<loan_pda>/payments', methods=['POST'])
async def make_payment(loan_pda):
    try:
        data = request.json
        client, program = await get_solana_client()
        
        payment_amount = data['paymentAmount']
        borrower_keypair = Keypair.from_secret_key(
            bytes(data['borrowerPrivateKey'])
        )

        tx = await program.rpc["make_payment"](
            payment_amount,
            accounts={
                'loanAccount': PublicKey(loan_pda),
                'borrower': borrower_keypair.public_key,
                'lender': program.provider.wallet.public_key,
            },
            signers=[borrower_keypair]
        )

        # Get updated loan info
        loan_account = await program.account["LoanAccount"].fetch(
            PublicKey(loan_pda)
        )

        return jsonify({
            'success': True,
            'transaction': str(tx),
            'loanStatus': {
                'paidAmount': str(loan_account.paid_amount),
                'isActive': loan_account.is_active
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Get loan details endpoint
@app.route('/api/loans/<loan_pda>', methods=['GET'])
async def get_loan(loan_pda):
    try:
        client, program = await get_solana_client()
        
        loan_account = await program.account["LoanAccount"].fetch(
            PublicKey(loan_pda)
        )

        return jsonify({
            'success': True,
            'loan': {
                'lender': str(loan_account.lender),
                'borrower': str(loan_account.borrower),
                'amount': str(loan_account.amount),
                'apy': loan_account.apy,
                'paidAmount': str(loan_account.paid_amount),
                'startTime': loan_account.start_time,
                'duration': loan_account.duration,
                'isActive': loan_account.is_active
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ✅ Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)

