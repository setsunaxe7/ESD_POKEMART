from flask import Flask, request, jsonify
import stripe
import os
from flask_cors import CORS
import logging
from pymongo import MongoClient


logging.basicConfig(level = logging.INFO)
app = Flask(__name__)
CORS(app)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

# Database & Collection
db = client["payment_db"]  # Database Name
bids_collection = db["payment"]  # Collection Name


@app.route("/create_payment_intent", methods=["POST"])
def create_payment_intent():
    try:
        # Extract Authorization header and JWT token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization header missing or invalid"}), 401

        jwt_token = auth_header.split(" ")[1]  # Extract the token part
        logging.info(f"Extracted JWT Token: {jwt_token}")

        # Decode JWT token to extract user ID (assuming no signature verification for simplicity)
        try:
            decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
            user_id = decoded_token.get("sub")  # Extract user ID (subject)
            if not user_id:
                return jsonify({"error": "User ID missing in JWT token"}), 401
        except Exception as e:
            logging.error(f"Error decoding JWT token: {e}")
            return jsonify({"error": "Invalid JWT token"}), 401

        logging.warning(f"Received request data: {request.json}")  # Log incoming request data

        # Extract payment data from request
        data = request.json
        amount = data.get("amount")  # Amount in cents (e.g., $10 -> 1000)
        currency = data.get("currency", "usd")  # Default to USD

        # Validate amount
        if not amount or not isinstance(amount, int) or amount <= 0:
            return jsonify({"error": "Invalid amount. Amount must be a positive integer in cents."}), 400

        # Validate currency
        if not isinstance(currency, str) or len(currency) != 3:
            return jsonify({"error": "Invalid currency. Currency must be a valid ISO 4217 code (e.g., 'usd')."}), 400

        # Create a payment intent using Stripe's API
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method_types=["card"]
        )

        print(f"Created PaymentIntent: {payment_intent.id}")  # Log successful PaymentIntent creation

        # Store payment data in MongoDB
        payment_data = {
            "user_id": user_id,                    # User ID from Supabase JWT token
            "payment_intent_id": payment_intent.id,  # Stripe PaymentIntent ID
            "amount": amount,                      # Payment amount in cents
            "currency": currency,                  # Currency code (e.g., usd)
            "status": payment_intent.status,       # Stripe PaymentIntent status
            "created_at": payment_intent.created,  # Timestamp when PaymentIntent was created
            "metadata": payment_intent.metadata    # Metadata from PaymentIntent (if any)
        }
        
        result = bids_collection.insert_one(payment_data)  # Insert into MongoDB collection
        logging.info(f"Payment data stored in DB with ID: {result.inserted_id}")

        return jsonify({"clientSecret": payment_intent.client_secret}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Log unexpected errors
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    try:
        data = request.json
        logging.warning(f"Received request data: {data}")  # Log incoming request data

        amount = data.get("amount")  # Amount in cents (e.g., $10 -> 1000)
        currency = data.get("currency", "usd")  # Default to USD

        # Validate amount
        if not amount or not isinstance(amount, int) or amount <= 0:
            return jsonify({"error": "Invalid amount. Amount must be a positive integer in cents."}), 400

        # Validate currency
        if not isinstance(currency, str) or len(currency) != 3:
            return jsonify({"error": "Invalid currency. Currency must be a valid ISO 4217 code (e.g., 'usd')."}), 400

        # Create a payment intent using Stripe's API
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method_types=["card"]
        )

        print(f"Created PaymentIntent: {payment_intent.id}")  # Log successful PaymentIntent creation
        return jsonify({"clientSecret": payment_intent.client_secret}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Log unexpected errors
        return jsonify({"error": f"Server error: {str(e)}"}), 500

    

@app.route("/refund", methods=["POST"])
def create_refund():
    try:
        data = request.json
        charge_id = data.get("charge_id")  # ID of the charge to refund
        payment_intent_id = data.get("payment_intent_id")  # ID of the PaymentIntent to refund (optional)
        amount = data.get("amount")  # Amount to refund (optional)
        reason = data.get("reason")  # Reason for refund (optional)

        if not charge_id and not payment_intent_id:
            return jsonify({"error": "Either 'charge_id' or 'payment_intent_id' must be provided"}), 400

        # Create a refund via Stripe API
        refund_data = {
            "amount": amount,
            "reason": reason,
            "metadata": {"source": "payment_microservice"}
        }

        if charge_id:
            refund_data["charge"] = charge_id
        elif payment_intent_id:
            refund_data["payment_intent"] = payment_intent_id

        refund = stripe.Refund.create(**refund_data)

        return jsonify({"refund": refund}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007)
