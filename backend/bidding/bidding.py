from flask import Flask, request, jsonify
from pymongo import MongoClient
import redis
import os
import json
import pika
from flask_cors import CORS
import amqp_lib


app = Flask(__name__)
CORS(app)

# Load MongoDB connection string from environment variables
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

# Database & Collection
db = client["bidding_db"]  # Database Name
bids_collection = db["bids"]  # Collection Name

# Redis Connection
redis_client = redis.StrictRedis(host="redis-cache-service", port=6379, decode_responses=True)

###############################################################################################

# RabbitMQ Config
rabbit_host = "rabbitmq"  # Use "rabbitmq" if running inside Docker
rabbit_port = 5672
exchange_name = "grading_topic"  # Topic exchange declared in amqp_setup.py
exchange_type = "topic"
queue_name = "auction"  # Queue for auction updates



# AMQP message for updating bid data
def send_bid_update(listing_id, highest_bid):
    try:
        # Establish connection to RabbitMQ using amqp_lib
        connection, channel = amqp_lib.connect(
            hostname=rabbit_host,
            port=rabbit_port,
            exchange_name=exchange_name,
            exchange_type=exchange_type,
        )

        # Publish bid update to RabbitMQ with a routing key
        routing_key = f"update.auction"  # Routing key for auction updates
        message = json.dumps({'listing_id': listing_id, 'highest_bid': highest_bid})
        channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message)

        print(f"Sent bid update: {message} with routing key: {routing_key}")
    except Exception as e:
        print(f"Error sending bid update: {e}")
    finally:
        # Close the connection and channel using amqp_lib
        amqp_lib.close(connection, channel)


# Prepopulate redis cache via MongoDB on startup
def populate_redis_cache():
    print("Populating Redis cache with highest bids from MongoDB...")
    auctions = bids_collection.aggregate([
        {"$group": {"_id": "$auctionId", "highestBid": {"$max": "$bidAmount"}}}
    ])
    for auction in auctions:
        auction_id = auction["_id"]
        highest_bid = auction["highestBid"]
        redis_client.set(auction_id, highest_bid)
        print(f"Cached auction {auction_id} with highest bid {highest_bid}")

###############################################################################################


# POST route to place a bid
@app.route("/bid", methods=["POST"])
def place_bid():
    data = request.json
    auction_id = data.get("auctionId")
    bid_amount = float(data.get("bidAmount"))  # Ensure it's a float
    bidder_id = data.get("buyerId")
    timestamp = data.get("timestamp")

    if not all([auction_id, bid_amount, bidder_id]):
        return jsonify({"error": "Missing required fields"}), 400

    # Check the highest bid from Redis cache first
    cached_highest = redis_client.get(auction_id)
    current_highest = float(cached_highest) if cached_highest else 0

    if bid_amount <= current_highest:
        return jsonify({"error": "Bid must be higher than the current highest bid"}), 400

    # Store the new bid in MongoDB
    new_bid = {
        "auctionId": auction_id,
        "buyerId": bidder_id,
        "bidAmount": bid_amount,
        "timestamp": timestamp,
    }
    bids_collection.insert_one(new_bid)

    # Update Redis cache with the new highest bid
    redis_client.set(auction_id, bid_amount)
    send_bid_update(auction_id, bid_amount)


    return jsonify({"message": "Bid placed successfully", "newHighest": bid_amount}), 201


# GET route to fetch the highest bid for an auction
@app.route("/highest-bid/<auction_id>", methods=["GET"])
def get_highest_bid(auction_id):
    # Check Redis cache first
    cached_highest = redis_client.get(auction_id)
    
    if cached_highest:
        return jsonify({"auctionId": auction_id, "highestBid": float(cached_highest)})

    # If not cached, fetch from MongoDB
    highest_bid_entry = bids_collection.find_one(
        {"auctionId": auction_id}, sort=[("bidAmount", -1)]
    )
    highest_bid = highest_bid_entry["bidAmount"] if highest_bid_entry else 0

    # Store in Redis for future use
    redis_client.set(auction_id, highest_bid)

    return jsonify({"auctionId": auction_id, "highestBid": highest_bid})


# GET route to fetch all bids for an auction
@app.route("/bids/<auction_id>", methods=["GET"])
def get_bids(auction_id):
    bids = list(bids_collection.find({"auctionId": auction_id}, {"_id": 0}))  # Hide MongoDB _id
    return jsonify({"bids": bids})


if __name__ == "__main__":
    populate_redis_cache()
    app.run(host="0.0.0.0", port=5002, debug=True)
