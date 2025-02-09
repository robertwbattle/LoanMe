from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_post, get_user, get_payment_schedule, get_transaction, get_payment
from db import create_post, create_user, create_transaction, create_payment
import sqlite3
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from anchorpy import Provider, Wallet
from solana.rpc.commitment import Confirmed
from solders.instruction import Instruction, AccountMeta
from solders.system_program import ID as SYS_PROGRAM_ID, TransferParams, transfer
from solders.message import Message
from solana.transaction import Transaction
import asyncio
from base64 import b64encode
import json
import os
import logging
from solana.rpc.types import TxOpts
from functools import wraps

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# BPF Loader program ID (this is the standard BPF loader on Solana)
BPF_LOADER_ID = Pubkey.from_string("BPFLoader2111111111111111111111111111111111")
CHUNK_SIZE = 800

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
    try:
        client = AsyncClient("https://api.devnet.solana.com")
        keypair = Keypair.from_bytes(bytes(json.loads(os.getenv("WALLET_PRIVATE_KEY"))))
        wallet = Wallet(keypair)
        provider = Provider(client, wallet)
        return client, None, wallet
    except Exception as e:
        logger.error(f"Error in get_solana_client: {str(e)}")
        raise

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
        SELECT p.post_type, p.loan_amount, p.status
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
        client, _, _ = await get_solana_client()
        
        borrower = Pubkey(data['borrowerPublicKey'])
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
        client, program, _ = await get_solana_client()
        
        payment_amount = data['paymentAmount']
        borrower_keypair = Keypair.from_secret_key(
            bytes(data['borrowerPrivateKey'])
        )

        tx = await program.rpc["make_payment"](
            payment_amount,
            accounts={
                'loanAccount': Pubkey(loan_pda),
                'borrower': borrower_keypair.public_key,
                'lender': program.provider.wallet.public_key,
            },
            signers=[borrower_keypair]
        )

        # Get updated loan info
        loan_account = await program.account["LoanAccount"].fetch(
            Pubkey(loan_pda)
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
        client, program, _ = await get_solana_client()
        
        loan_account = await program.account["LoanAccount"].fetch(
            Pubkey(loan_pda)
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

# Add this to handle async routes in Flask
def async_route(route_function):
    def wrapper(*args, **kwargs):
        return asyncio.run(route_function(*args, **kwargs))
    wrapper.__name__ = route_function.__name__
    return wrapper

# Modify the deploy endpoint with the decorator
@app.route('/api/deploy', methods=['POST'])
@async_route
async def deploy_contract():
    try:
        logger.info("Starting deployment...")
        
        # Check program file exists
        program_path = '../anchor/target/deploy/sol_backend.so'
        if not os.path.exists(program_path):
            return jsonify({'success': False, 'error': 'Program file not found'}), 404
            
        # Get client and program data
        client, _, wallet = await get_solana_client()
        with open(program_path, 'rb') as f:
            program_data = f.read()
        
        # Create program keypair and get rent
        program_keypair = Keypair()
        program_len = len(program_data)
        rent = await client.get_minimum_balance_for_rent_exemption(program_len)
        
        # Create program account instruction
        create_account_ix = Instruction(
            program_id=SYS_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=wallet.public_key, is_signer=True, is_writable=True),
                AccountMeta(pubkey=program_keypair.pubkey(), is_signer=True, is_writable=True),
            ],
            data=(
                bytes([0]) +  # Create account instruction
                rent.value.to_bytes(8, 'little') +  # Lamports
                program_len.to_bytes(8, 'little') +  # Space
                bytes(BPF_LOADER_ID)  # Owner
            )
        )
        
        # Send create account transaction
        recent_blockhash = await client.get_latest_blockhash()
        create_tx = Transaction()
        create_tx.add(create_account_ix)
        create_tx.recent_blockhash = recent_blockhash.value.blockhash
        
        create_response = await client.send_transaction(
            create_tx,
            wallet.payer,
            program_keypair,
            opts=TxOpts(skip_preflight=True)
        )
        logger.info(f"Account created: {str(create_response.value)}")
        
        # Add delay after account creation
        await asyncio.sleep(1)
        
        # Write program data in chunks
        CHUNK_SIZE = 900
        chunks = [program_data[i:i + CHUNK_SIZE] for i in range(0, len(program_data), CHUNK_SIZE)]
        write_responses = []
        
        for i, chunk in enumerate(chunks):
            try:
                write_ix = Instruction(
                    program_id=BPF_LOADER_ID,
                    accounts=[
                        AccountMeta(pubkey=wallet.public_key, is_signer=True, is_writable=True),
                        AccountMeta(pubkey=program_keypair.pubkey(), is_signer=True, is_writable=True),
                    ],
                    data=bytes([1]) + i.to_bytes(4, 'little') + chunk
                )
                
                write_tx = Transaction()
                write_tx.add(write_ix)
                write_tx.recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
                
                write_response = await client.send_transaction(
                    write_tx,
                    wallet.payer,
                    program_keypair,
                    opts=TxOpts(skip_preflight=True)
                )
                write_responses.append(str(write_response.value))
                logger.info(f"Chunk {i+1}/{len(chunks)} written")
                
                # Add delay between chunks to avoid rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error writing chunk {i}: {str(e)}")
                # If we hit rate limit, wait longer and retry
                if "429" in str(e):
                    logger.info("Rate limit hit, waiting 2 seconds...")
                    await asyncio.sleep(2)
                    # Retry the chunk
                    i -= 1
                    continue
                raise e
            
        # Add delay before finalize
        await asyncio.sleep(1)
        
        # Finalize the deployment
        finalize_ix = Instruction(
            program_id=BPF_LOADER_ID,
            accounts=[
                AccountMeta(pubkey=wallet.public_key, is_signer=True, is_writable=True),
                AccountMeta(pubkey=program_keypair.pubkey(), is_signer=True, is_writable=True),
            ],
            data=bytes([2])  # Finalize instruction
        )
        
        finalize_tx = Transaction()
        finalize_tx.add(finalize_ix)
        finalize_tx.recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
        
        finalize_response = await client.send_transaction(
            finalize_tx,
            wallet.payer,
            program_keypair,
            opts=TxOpts(skip_preflight=True)
        )
        logger.info("Program deployment finalized")
        
        return jsonify({
            'success': True,
            'programId': str(program_keypair.pubkey()),
            'createTx': str(create_response.value),
            'writeTxs': write_responses,
            'finalizeTx': str(finalize_response.value)
        })
        
    except Exception as e:
        logger.error(f"Deployment error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Get deployment status
@app.route('/api/deploy/<signature>', methods=['GET'])
async def get_deploy_status(signature):
    try:
        client, _, _ = await get_solana_client()
        status = await client.get_transaction(signature)
        
        return jsonify({
            'success': True,
            'status': status['result']['meta']['status'],
            'confirmations': status['result']['confirmations']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/wallet/balance', methods=['GET'])
@async_route
async def get_wallet_balance():
    try:
        client, _, wallet = await get_solana_client()
        balance_response = await client.get_balance(wallet.public_key)
        
        return jsonify({
            'success': True,
            'balance': balance_response.value / 1e9,  # Convert lamports to SOL
            'balance_lamports': balance_response.value
        })
        
    except Exception as e:
        logger.error(f"Error getting balance: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/wallet/address', methods=['GET'])
@async_route
async def get_wallet_address():
    try:
        _, _, wallet = await get_solana_client()
        return jsonify({
            'success': True,
            'address': str(wallet.public_key)
        })
        
    except Exception as e:
        logger.error(f"Error getting wallet address: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/wallet/transfer', methods=['POST'])
@async_route
async def transfer_sol():
    try:
        logger.info("Starting SOL transfer...")
        data = request.json
        if not data or 'destination' not in data or 'amount' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing destination or amount in request'
            }), 400
            
        client, _, wallet = await get_solana_client()
        
        # Convert SOL to lamports
        amount_sol = float(data['amount'])
        amount_lamports = int(amount_sol * 1e9)
        
        # Create destination pubkey
        destination = Pubkey.from_string(data['destination'])
        logger.info(f"Transferring {amount_sol} SOL to {destination}")
        
        # Create transfer instruction
        transfer_ix = transfer(
            TransferParams(
                from_pubkey=wallet.public_key,
                to_pubkey=destination,
                lamports=amount_lamports
            )
        )
        
        # Get recent blockhash
        recent_blockhash = await client.get_latest_blockhash()
        
        # Create transaction
        tx = Transaction()
        tx.add(transfer_ix)
        tx.recent_blockhash = recent_blockhash.value.blockhash
        tx.fee_payer = wallet.public_key
        
        # Send transaction with signer
        logger.info("Sending transaction with signer...")
        opts = TxOpts(skip_preflight=True, preflight_commitment=Confirmed)
        signature = await client.send_transaction(
            tx, 
            wallet.payer,
            opts=opts
        )
        logger.info(f"Transfer complete. Signature: {signature}")
        
        return jsonify({
            'success': True,
            'signature': str(signature.value),
            'amount': amount_sol,
            'destination': str(destination)
        })
        
    except Exception as e:
        logger.error(f"Error transferring SOL: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
    
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE email = ? AND password_hash = ?", (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True, "user": {"user_id": user[0], "email": user[2], "score": user[3], "solana_address": user[5]}})
    else:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401


@app.route('/api/program/<program_id>', methods=['GET'])
@async_route
async def get_program_info(program_id):
    try:
        client, _, _ = await get_solana_client()
        program_info = await client.get_account_info(Pubkey.from_string(program_id))
        
        return jsonify({
            'success': True,
            'exists': program_info.value is not None,
            'executable': program_info.value.executable if program_info.value else False,
            'lamports': program_info.value.lamports if program_info.value else 0,
            'owner': str(program_info.value.owner) if program_info.value else None,
            'data_len': len(program_info.value.data) if program_info.value else 0
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ✅ Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)

