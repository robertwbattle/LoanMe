# In app.py (or equivalent backend file)
from flask import Flask, jsonify

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    conn = sqlite3.connect('loan_platform.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    conn.close()

    if post:
        return jsonify({
            "id": post[0],
            "account_name": post[1],
            "loan_amount": post[2],
            "interest_rate": post[3],
            "payment_schedule": post[4],
            "description": "Detailed information about this loan post."  # Example
        })
    return jsonify({"error": "Post not found"}), 404
