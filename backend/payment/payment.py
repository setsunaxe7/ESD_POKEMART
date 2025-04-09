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
        logging.info(f"Received request data: {request.json}")  # Log incoming request data

        # Extract payment data from request
        data = request.json
        amount = data.get("amount")  # Amount in cents (e.g., $10 -> 1000)
        currency = data.get("currency", "usd")  # Default to USD
        user_id = data.get("userId")
        listing_id = data.get("listingId")

        # Validate amount
        if not amount or not isinstance(amount, int) or amount <= 0:
            return jsonify({"error": "Invalid amount. Amount must be a positive integer in cents."}), 400

        # Validate currency
        if not isinstance(currency, str) or len(currency) != 3:
            return jsonify({"error": "Invalid currency. Currency must be a valid ISO 4217 code (e.g., 'usd')."}), 400

        # Step 1: Check if listing is active
        listing = supabase.table('marketplace').select('*').eq('id', listing_id).execute().data
        if not listing or listing[0].get("status") != "active":
            return jsonify({"error": "Listing is no longer available for purchase"}), 400

        # Create a payment intent using Stripe's API
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method_types=["card"]
        )

        print(f"Created PaymentIntent: {payment_intent.id}")  # Log successful PaymentIntent creation

        # Store payment data in MongoDB
        payment_data = {
            "user_id": user_id,                    # buyer id
            "listing_id": listing_id,              # listing id
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


@app.route("/update_payment_status", methods=["PUT"])
def update_payment_status():
    try:
        # Extract data from request
        data = request.json
        payment_intent_id = data.get("payment_intent_id")
        status = data.get("status")

        # Validate input
        if not payment_intent_id or not status:
            return jsonify({"error": "Missing required fields"}), 400

        # Update payment status in MongoDB
        result = bids_collection.update_one(
            {"payment_intent_id": payment_intent_id},
            {"$set": {"status": status}}
        )

        if result.matched_count == 0:
            return jsonify({"error": "PaymentIntent not found"}), 404

        return jsonify({"message": "Payment status updated successfully"}), 200

    except Exception as e:
        logging.error(f"Error occurred while updating payment status: {e}")
        return jsonify({"error": str(e)}), 500




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

        # Update payment status in MongoDB using the existing route logic
        result = bids_collection.update_one(
            {"payment_intent_id": payment_intent_id},
            {"$set": {"status": "refunded"}}
        )

        if result.matched_count == 0:
            return jsonify({"error": "PaymentIntent not found"}), 404


        return jsonify({"refund": refund}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ...existing code...

@app.route("/payments/<user_id>", methods=["GET"])
def get_user_payments(user_id):
    try:
        # Validate user_id
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Query MongoDB for payments with the given user_id
        payments = list(bids_collection.find({"user_id": user_id}, {"_id": 0}))

        if not payments:
            return jsonify({"message": "No payments found for this user", "payments": []}), 200

        # Convert non-serializable objects to string (like ObjectId)
        for payment in payments:
            if 'created_at' in payment:
                payment['created_at'] = str(payment['created_at'])

        logging.info(f"Retrieved {len(payments)} payments for user {user_id}")

        return jsonify({"payments": payments}), 200

    except Exception as e:
        logging.error(f"Error retrieving payments for user {user_id}: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007)
