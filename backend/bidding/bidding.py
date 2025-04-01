from flask import Flask, request, jsonify
from pymongo import MongoClient
import redis
import os
import json
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Load MongoDB connection string from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

# Database & Collection
db = client["bidding_db"]  # Database Name
bids_collection = db["bids"]  # Collection Name

# Redis Connection
redis_client = redis.StrictRedis(host="redis-cache-service", port=6379, decode_responses=True)

# POST route to place a bid
@app.route("/bid", methods=["POST"])
def place_bid():
    data = request.json
    auction_id = data.get("auctionId")
    bid_amount = float(data.get("bidAmount"))  # Ensure it's a float
    bidder_id = data.get("buyerId")

    if not all([auction_id, bid_amount, bidder_id]):
        return jsonify({"error": "Missing required fields"}), 400

    # Check the highest bid from Redis cache first
    cached_highest = redis_client.get(f"highest_bid:{auction_id}")
    current_highest = float(cached_highest) if cached_highest else 0

    if bid_amount <= current_highest:
        return jsonify({"error": "Bid must be higher than the current highest bid"}), 400

    # Store the new bid in MongoDB
    new_bid = {
        "auctionId": auction_id,
        "buyerId": bidder_id,
        "price": bid_amount
    }
    bids_collection.insert_one(new_bid)

    # Update Redis cache with the new highest bid
    redis_client.set(f"highest_bid:{auction_id}", bid_amount)

    return jsonify({"message": "Bid placed successfully", "newHighest": bid_amount}), 201


# GET route to fetch the highest bid for an auction
@app.route("/highest-bid/<auction_id>", methods=["GET"])
def get_highest_bid(auction_id):
    # Check Redis cache first
    cached_highest = redis_client.get(f"highest_bid:{auction_id}")
    
    if cached_highest:
        return jsonify({"auctionId": auction_id, "highestBid": float(cached_highest)})

    # If not cached, fetch from MongoDB
    highest_bid_entry = bids_collection.find_one(
        {"auctionId": auction_id}, sort=[("price", -1)]
    )
    highest_bid = highest_bid_entry["price"] if highest_bid_entry else 0

    # Store in Redis for future use
    redis_client.set(f"highest_bid:{auction_id}", highest_bid)

    return jsonify({"auctionId": auction_id, "highestBid": highest_bid})


# GET route to fetch all bids for an auction
@app.route("/bids/<auction_id>", methods=["GET"])
def get_bids(auction_id):
    bids = list(bids_collection.find({"auctionId": auction_id}, {"_id": 0}))  # Hide MongoDB _id
    return jsonify({"bids": bids})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
