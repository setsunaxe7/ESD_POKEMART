from flask import Flask, request, jsonify
import requests
import pika
import json

app = Flask(__name__)

# Marketplace API endpoint
MARKETPLACE_API_URL = "http://marketplace-service/api/auction"

# RabbitMQ Connection (for AMQP messaging)
RABBITMQ_HOST = "rabbitmq"  # Use the service name in Docker
QUEUE_NAME = "new_bid"

def publish_new_bid(auction_id, buyer_id, price):
    """Publishes a NewBidPlaced event to RabbitMQ."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    message = {
        "auction_id": auction_id,
        "buyer_id": buyer_id,
        "price": price
    }

    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make the message persistent
        ),
    )
    connection.close()

@app.route("/bid", methods=["POST"])
def place_bid():
    """Handles new bid placements from the frontend."""
    data = request.json
    auction_id = data.get("auctionId")
    buyer_id = data.get("buyerId")
    price = data.get("price")

    if not auction_id or not buyer_id or not price:
        return jsonify({"error": "Missing required fields"}), 400

    # Send PUT request to Marketplace Microservice
    marketplace_response = requests.put(
        f"{MARKETPLACE_API_URL}/{auction_id}",
        json={"buyerId": buyer_id, "price": price},
    )

    if marketplace_response.status_code != 200:
        return jsonify({"error": "Failed to update auction"}), 500

    # Publish NewBidPlaced event
    publish_new_bid(auction_id, buyer_id, price)

    return jsonify({"message": "Bid placed successfully"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
