from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_post, get_user, get_payment_schedule, get_transaction, get_payment
from db import create_post, create_user, create_transaction, create_payment, update_user_solana_address, update_user_solana_private_key, add_payment_schedule
import sqlite3
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from anchorpy import Provider, Wallet, Context, Program
from solana.rpc.commitment import Confirmed
from solders.instruction import Instruction, AccountMeta
from solders.system_program import (
    create_account,
    CreateAccountParams,
    ID as SYS_PROGRAM_ID,
    TransferParams,
    transfer
)
from solders.message import Message
from solana.transaction import Transaction
import asyncio
from base64 import b64encode
import json
import os
import logging
from solana.rpc.types import TxOpts
import requests
import time
import time
from dotenv import load_dotenv
from anchorpy_core.idl import Idl
from idl import idl
from base58 import b58decode
from functools import wraps
from solders.sysvar import RENT as SYSVAR_RENT_PUBKEY
import struct

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# BPF Loader program ID (this is the standard BPF loader on Solana)
BPF_LOADER_ID = Pubkey.from_string("BPFLoader2111111111111111111111111111111111")
CHUNK_SIZE = 800

load_dotenv()  # Load .env file

def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

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
    
    # Load wallet from .env
    private_key_str = os.getenv('WALLET_PRIVATE_KEY')
    private_key = json.loads(private_key_str)
    wallet_keypair = Keypair.from_bytes(bytes(private_key))
    
    # Create Wallet wrapper that has the correct public_key property
    from anchorpy.provider import Wallet, Provider
    wallet = Wallet(wallet_keypair)
    
    # Load program ID from .env
    program_id = Pubkey.from_string(os.getenv('PROGRAM_ID'))
    
    # Create provider
    provider = Provider(client, wallet)
    
    # Update IDL with correct program ID
    idl_copy = idl.copy()
    idl_copy['metadata'] = {'address': str(program_id)}
    
    # Convert dictionary to proper Idl object
    idl_obj = Idl.from_json(json.dumps(idl_copy))
    
    # Create program with proper Idl object
    program = Program(idl_obj, program_id, provider)
    
    return client, program, wallet

# ✅ Existing API - Get a Single Loan
@app.route('/api/loans/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Loans WHERE loan_id = ?", (loan_id,))
    loan = cursor.fetchone()
    conn.close()

    if loan:
        return jsonify({
            "loan_id": loan[0],
            "account_name": loan[1],
            "loan_amount": loan[2],
            "interest_rate": loan[3],
            "payment_schedule": loan[4],
            "description": "Detailed information about this loan."
        })
    return jsonify({"error": "Loan not found"}), 404


# ✅ New API - Get All Loans
@app.route('/api/loans', methods=['GET'])
def get_loans():
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()

    # Simplified Query (No Joins)
    cursor.execute("SELECT loan_id, loan_amount, interest_rate, status FROM Loans WHERE status = 'open'")
    loans = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "id": loan[0],
            "loan_amount": loan[1],
            "interest_rate": loan[2],
            "status": loan[3]
        }
        for loan in loans
    ])


@app.route('/api/activity', methods=['GET'])
def get_activity():
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()

    # Example: Fetch user's loans as activity
    cursor.execute("""
        SELECT l.loan_type, l.loan_amount, l.status
        FROM Loans l
        JOIN Users u ON l.user_id = u.user_id
        ORDER BY l.created_at DESC
    """)
    activities = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "type": loan[0],                # borrow/lend
            "details": f"Loan of ${loan[1]} ({loan[2]}) by {loan[3]}"
        }
        for loan in activities
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

            print(wallet_data)
            
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
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            create_user(password, email, None, None)
            
            # Generate wallet for the new user
            user_id = get_user_id_by_email(email)
            wallet_response = generate_wallet(user_id)
            wallet_result = wallet_response.get_json()
            if wallet_result['success']:
                update_user_solana_address(user_id, wallet_result['wallet']['address'])
                update_user_solana_private_key(user_id, wallet_result['wallet']['private_key'])
            
            return jsonify({"success": True, "message": "Account created successfully"})
        except Exception as e:
            logger.error(f"Error creating account: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

def get_user_id_by_email(email):
    try:
        conn = sqlite3.connect('loan_platform.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM Users WHERE email = ?", (email,))
        user_id = cursor.fetchone()[0]
        conn.close()
        return user_id
    except Exception as e:
        logger.error(f"Error getting user ID by email: {str(e)}")
        raise

def _build_cors_preflight_response():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

# Make payment endpoint
@app.route('/api/loans/<loan_pda>/payments', methods=['POST'])
@async_route
async def make_payment(loan_pda):
    try:
        data = request.json
        client, program, _ = await get_solana_client()
        
        # Convert borrower's private key to keypair
        if 'borrowerPrivateKey' not in data:
            return jsonify({
                'success': False,
                'error': 'Borrower private key is required'
            }), 400
            
        try:
            borrower_keypair = Keypair.from_base58_string(data['borrowerPrivateKey'])
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Invalid borrower private key: {str(e)}'
            }), 400
        
        # Verify the borrower's public key matches
        if str(borrower_keypair.pubkey()) != data['borrowerPublicKey']:
            return jsonify({
                'success': False,
                'error': 'Borrower signature does not match public key'
            }), 400
        
        lender = Pubkey.from_string(data['lenderPublicKey'])
        payment_amount = int(data['paymentAmount'])
        loan_pda_pubkey = Pubkey.from_string(loan_pda)
        
        # Create provider with borrower's wallet
        provider = Provider(
            client,
            Wallet(borrower_keypair),
            opts=None
        )
        
        # Create program instance with borrower's provider
        program = Program(program.idl, program.program_id, provider)
        
        # Fetch and validate loan account
        try:
            loan_account = await program.account["LoanAccount"].fetch(loan_pda_pubkey)
            
            if not loan_account.is_active:
                return jsonify({
                    'success': False,
                    'error': 'Loan is not active'
                }), 400
                
            if loan_account.borrower != borrower_keypair.pubkey():
                return jsonify({
                    'success': False,
                    'error': 'Only the borrower can make payments'
                }), 403
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to fetch loan account: {str(e)}'
            }), 404
        
        ctx = Context(
            accounts={
                'loanAccount': loan_pda_pubkey,
                'lender': lender,
                'borrower': borrower_keypair.pubkey(),
                'system_program': SYS_PROGRAM_ID,
            },
            signers=[borrower_keypair],  # Include borrower's keypair for signing
            remaining_accounts=[],
            pre_instructions=[],
            post_instructions=[],
        )
        
        logger.info(f"Making payment of {payment_amount} lamports to loan {loan_pda}")
        
        tx = await program.rpc["make_payment"](
            payment_amount,
            ctx=ctx
        )
        
        logger.info(f"Payment transaction sent: {tx}")
        
        # Fetch updated loan info
        updated_loan = await program.account["LoanAccount"].fetch(loan_pda_pubkey)
        
        return jsonify({
            'success': True,
            'transaction': str(tx),
            'loanStatus': {
                'paidAmount': str(updated_loan.paid_amount),
                'isActive': updated_loan.is_active
            }
        })
        
    except Exception as e:
        logger.error(f"Error making payment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Get loan details endpoint
@app.route('/api/loans/<loan_pda>', methods=['GET'])
async def get_loan_details(loan_pda):
    try:
        client, program, wallet = await get_solana_client()
        
        loan_account = await program.account["LoanAccount"].fetch(
            Pubkey.from_string(loan_pda)
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
        logger.error(f"Error fetching loan: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Modify the deploy endpoint with the decorator
@app.route('/api/deploy', methods=['POST'])
@async_route
async def deploy_contract():
    try:
        logger.info("=== Starting deployment process ===")

        borrower_id = request.json.get('borrower_id')
        if borrower_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE Users
                SET borrow_count = borrow_count + 1
                WHERE user_id = ?
            ''', (borrower_id,))
            conn.commit()
            conn.close()

        return jsonify({
            'message': 'borrow count updated.'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
        # Get client and wallet
        client, _, wallet = await get_solana_client()
        
        # Check program file and read it
        program_path = '../anchor/target/deploy/sol_backend.so'
        if not os.path.exists(program_path):
            logger.error(f"Program file not found at {program_path}")
            return jsonify({
                'success': False,
                'error': f"Program file not found at {program_path}"
            }), 404
            
        client, _, wallet = await get_solana_client()
        logger.info(f"Got client and wallet. Wallet pubkey: {wallet.public_key}")
        
        # Read program
        with open(program_path, 'rb') as f:
            program_data = f.read()
        logger.info(f"Program data size: {len(program_data)} bytes")
        logger.info(f"Read program binary, size: {len(program_data)} bytes")
        
        # Create program keypair
        program_keypair = Keypair()
        logger.info(f"New program ID: {program_keypair.pubkey()}")
        
        # Get minimum rent
        program_len = len(program_data)
        rent = await client.get_minimum_balance_for_rent_exemption(program_len)
        logger.info(f"Required rent: {rent.value} lamports")
        
        # Create account
        create_account_ix = Instruction(
            program_id=SYS_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=wallet.public_key, is_signer=True, is_writable=True),
                AccountMeta(pubkey=program_keypair.pubkey(), is_signer=False, is_writable=True),
            ],
            data=bytes([0, 0, 0, 0])  # create account instruction index
        )
        
        # Send create transaction
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
        
        # Wait for confirmation
        await client.confirm_transaction(create_response.value)
        logger.info("Account creation confirmed")
        
        # Write program in smaller chunks
        CHUNK_SIZE = 500  # Reduced from 800
        chunks = [program_data[i:i + CHUNK_SIZE] for i in range(0, len(program_data), CHUNK_SIZE)]
        write_responses = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Writing chunk {i+1}/{len(chunks)} (size: {len(chunk)} bytes)")
            write_ix = Instruction(
                program_id=BPF_LOADER_ID,
                accounts=[
                    AccountMeta(pubkey=wallet.public_key, is_signer=True, is_writable=True),
                    AccountMeta(pubkey=program_keypair.pubkey(), is_signer=False, is_writable=True),
                ],
                data=bytes([1]) + i.to_bytes(4, 'little') + chunk
            )
            
            write_tx = Transaction()
            write_tx.add(write_ix)
            write_tx.recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
            
            write_response = await client.send_transaction(
                write_tx,
                wallet.payer,
                opts=TxOpts(skip_preflight=True)
            )
            write_responses.append(str(write_response.value))
            
            # Wait for confirmation of each chunk
            await client.confirm_transaction(write_response.value)
            logger.info(f"Chunk {i+1} confirmed")
            await asyncio.sleep(1)
            
        logger.info("All chunks written successfully")
        
        # Finalize program
        finalize_ix = Instruction(
            program_id=BPF_LOADER_ID,
            accounts=[
                AccountMeta(pubkey=wallet.public_key, is_signer=True, is_writable=True),
                AccountMeta(pubkey=program_keypair.pubkey(), is_signer=False, is_writable=True),
            ],
            data=bytes([2])
        )
        
        finalize_tx = Transaction()
        finalize_tx.add(finalize_ix)
        finalize_tx.recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
        
        finalize_response = await client.send_transaction(
            finalize_tx,
            wallet.payer,
            opts=TxOpts(skip_preflight=True)
        )
        
        # Wait for finalization
        await client.confirm_transaction(finalize_response.value)
        logger.info("Program finalized")
        
        return jsonify({
            'success': True,
            'programId': str(program_keypair.pubkey()),
            'createTx': str(create_response.value),
            'writeTxs': write_responses,
            'finalizeTx': str(finalize_response.value)
        })
        
    except Exception as e:
        logger.error(f"=== UNHANDLED ERROR IN DEPLOYMENT ===")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error message: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': str(type(e)),
            'traceback': traceback.format_exc()
        }), 500

# Get deployment status
@app.route('/api/deploy/<signature>', methods=['GET'])
async def get_deploy_status(signature):
    try:
        client, program_id, _ = await get_solana_client()
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
        client, program_id, wallet = await get_solana_client()
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
        _, program_id, wallet = await get_solana_client()
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
            
        client, program_id, wallet = await get_solana_client()
        
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
        
        # Sign transaction
        tx.sign(wallet.payer)
        
        # Send transaction with signer
        logger.info("Sending transaction with signer...")
        signature = await client.send_raw_transaction(tx.serialize())
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
        client  = await get_solana_client()
        program_info = await client[0].get_account_info(Pubkey.from_string(program_id))

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

@app.route('/api/user/<int:user_id>/loans', methods=['GET'])
def get_user_loans(user_id):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.loan_amount, l.interest_rate, l.payment_schedule, p.amount_due, p.amount_paid, p.payment_status
        FROM Loans l
        JOIN Payments p ON l.loan_id = p.loan_id
        WHERE l.user_id = ?
    ''', (user_id,))
    loans = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            'id': loan[0],
            'loan_amount': loan[1],
            'interest_rate': loan[2],
            'payment_schedule': loan[3],
            'amount_due': loan[4],
            'amount_paid': loan[5],
            'payment_status': loan[6],
        }
        for loan in loans
    ])

@app.route('/api/loans/<int:loan_id>/pay', methods=['POST'])
def pay_loan(loan_id):
    data = request.json
    amount = data.get('amount')
    borrow_id = data.get('borrower_id')
    if borrow_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Users
            SET successful_payments = successful_payments + 1
            WHERE user_id = ?
        ''', (borrow_id,))
        conn.commit()
        conn.close()

    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Payments
        SET amount_paid = amount_paid + ?, payment_status = 'paid'
        WHERE loan_id = ? AND payment_status = 'due'
    ''', (amount, loan_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Payment successful, successful_payments updated.'})

@app.route('/api/transactions', methods=['POST'])
def post_transaction_request():
    try:
        data = request.json
        lender_id = data['lender_id']
        borrower_id = data['borrower_id']
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        payment_schedule_id = data['payment_schedule_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert new post
        cursor.execute('''
            INSERT INTO Posts (user_id, post_type, loan_amount, interest_rate, payment_schedule_id, status)
            VALUES (?, 'lend', ?, ?, ?, 'open')
        ''', (lender_id, loan_amount, interest_rate, payment_schedule_id))

        conn.commit()
        post_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'success': True,
            'post_id': post_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API to accept a transaction request
@app.route('/api/transaction/accept', methods=['POST'])
def accept_transaction_request():
    try:
        data = request.json
        post_id = data['post_id']
        borrower_id = data['borrower_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get post details
        cursor.execute('SELECT user_id, loan_amount, interest_rate, payment_schedule_id FROM Posts WHERE post_id = ? AND status = "open"', (post_id,))
        post = cursor.fetchone()

        if not post:
            return jsonify({'success': False, 'error': 'Post not found or already funded.'}), 404

        lender_id, loan_amount, interest_rate, payment_schedule_id = post

        # Insert transaction
        cursor.execute('''
            INSERT INTO Transactions (lender_id, borrower_id, post_id, loan_amount, interest_rate, payment_schedule_id, status)
            VALUES (?, ?, ?, ?, ?, ?, 'active')
        ''', (lender_id, borrower_id, post_id, loan_amount, interest_rate, payment_schedule_id))

        # Update post status
        cursor.execute('UPDATE Posts SET status = "funded" WHERE post_id = ?', (post_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'transaction_id': cursor.lastrowid
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API to transfer money from lender to borrower
@app.route('/api/transaction/transfer', methods=['POST'])
def transfer_money():
    try:
        data = request.json
        transaction_id = data['transaction_id']
        blockchain_tx_id = data['blockchain_tx_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update transaction with blockchain transaction ID and mark as completed
        cursor.execute('''
            UPDATE Transactions
            SET blockchain_tx_id = ?, status = 'completed'
            WHERE transaction_id = ?
        ''', (blockchain_tx_id, transaction_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Money transferred successfully.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# API to transfer SOL using Solana API
@app.route('/api/solana/transfer', methods=['POST'])
@async_route
async def solana_transfer():
    try:
        data = request.json
        client, program, _ = await get_solana_client()
        
        logger.info("=== Starting SOL Transfer ===")
        logger.info(f"Request data: {data}")
        
        # Create keypair from private key
        private_key_bytes = bytes(data['private_key'])
        sender_keypair = Keypair.from_bytes(private_key_bytes)
        logger.info(f"Sender pubkey: {sender_keypair.pubkey()}")
        
        recipient = Pubkey.from_string(data['wallet_to'])
        amount_sol = float(data['transfer_amount'])
        amount_lamports = int(amount_sol * 1e9)  # Convert SOL to lamports
        
        logger.info(f"Transfer details:")
        logger.info(f"- Amount: {amount_sol} SOL ({amount_lamports} lamports)")
        logger.info(f"- Recipient: {recipient}")
        
        # Get recent blockhash
        recent_blockhash = await client.get_latest_blockhash()
        logger.info(f"Recent blockhash: {recent_blockhash.value.blockhash}")
        
        # Create transfer instruction
        transfer_ix = transfer(
            TransferParams(
                from_pubkey=sender_keypair.pubkey(),
                to_pubkey=recipient,
                lamports=amount_lamports
            )
        )
        
        # Create transaction
        tx = Transaction()
        tx.add(transfer_ix)
        tx.recent_blockhash = recent_blockhash.value.blockhash
        tx.fee_payer = sender_keypair.pubkey()
        
        # Sign transaction
        tx.sign(sender_keypair)
        
        # Send transaction
        logger.info("Sending transaction...")
        tx_sig = await client.send_raw_transaction(
            tx.serialize(),
            opts=TxOpts(skip_preflight=True)
        )
        
        # Wait for confirmation
        await client.confirm_transaction(tx_sig.value)
        logger.info(f"Transfer confirmed: {tx_sig.value}")
        
        return jsonify({
            'success': True,
            'signature': str(tx_sig.value),
            'amount': amount_sol,
            'recipient': str(recipient)
        })
        
    except Exception as e:
        logger.error(f"Error in solana_transfer: {str(e)}")
        logger.exception("Full traceback:")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/solana/balance/<wallet_address>', methods=['GET'])
@async_route
async def fetch_solana_balance(wallet_address):
    try:
        client, _, _ = await get_solana_client()
        
        # Convert address string to Pubkey
        pubkey = Pubkey.from_string(wallet_address)
        
        # Get balance
        balance = await client.get_balance(pubkey)
        balance_sol = balance.value / 1e9  # Convert lamports to SOL
        
        logger.info(f"Fetched balance for {wallet_address}: {balance_sol} SOL")
        
        return jsonify({
            'success': True,
            'wallet': wallet_address,
            'balance_lamports': balance.value,
            'balance_sol': balance_sol
        })
        
    except Exception as e:
        logger.error(f"Error fetching balance: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/loans', methods=['POST'])
def create_post():
    try:
        data = request.json
        logger.info("=== Creating New Post ===")
        logger.info(f"Request data: {data}")
        
        # Extract post details
        loan_amount = float(data['loan_amount'])
        interest_rate = float(data['interest_rate'])
        lender_wallet = data.get('lender_wallet')  # Optional for borrower posts
        borrower_wallet = data.get('borrower_wallet')  # Optional for lender posts
        
        # Validate that at least one wallet is provided
        if not lender_wallet and not borrower_wallet:
            return jsonify({
                'success': False,
                'error': 'At least one wallet (lender or borrower) must be provided'
            }), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert new post
        cursor.execute('''
            INSERT INTO Posts (
                lender_wallet,
                borrower_wallet,
                loan_amount,
                interest_rate,
                status
            )
            VALUES (?, ?, ?, ?, 'open')
        ''', (lender_wallet, borrower_wallet, loan_amount, interest_rate))
        
        post_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created post with ID: {post_id}")
        
        return jsonify({
            'success': True,
            'post_id': post_id,
            'details': {
                'lender_wallet': lender_wallet,
                'borrower_wallet': borrower_wallet,
                'loan_amount': loan_amount,
                'interest_rate': interest_rate,
                'status': 'open'
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        logger.exception("Full traceback:")
        return jsonify({'success': False, 'error': str(e)}), 500

# ✅ Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)


