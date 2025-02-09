from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_post, get_user, get_payment_schedule, get_transaction, get_payment
from db import create_post, create_user, create_transaction, create_payment
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

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

# ✅ Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)

