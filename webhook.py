import os
import sqlite3
import stripe
from flask import Flask, request
from dotenv import load_dotenv
from datetime import datetime

# Load keys
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("client_reference_id")
        price_id = session["metadata"].get("price_id")

        token_map = {
            "supporter": 10,
            "sustainer": 25,
            "patron": 50
        }
        tokens = token_map.get(price_id, 0)

        if user_id and tokens > 0:
            conn = sqlite3.connect("tokens.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_tokens (user_id, tokens_left, is_paid, last_reset)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    tokens_left = tokens_left + excluded.tokens_left,
                    is_paid = 1
            """, (user_id, tokens, datetime.now().date().isoformat()))
            conn.commit()
            conn.close()

    return "OK", 200

if __name__ == "__main__":
    app.run(port=4242)
