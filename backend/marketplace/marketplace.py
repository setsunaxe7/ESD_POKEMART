from flask import Flask, request, jsonify, json
from supabase import create_client
from werkzeug.utils import secure_filename
from flask_cors import CORS
import uuid
import os
import redis
import asyncio

# Initialize Flask app
app = Flask(__name__)
CORS(app)


# Supabase configuration

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

##############################################################################################################

# Connect to Redis
redis_client = redis.StrictRedis(host="redis-cache-service", port=6379, decode_responses=True)
pubsub = redis_client.pubsub()
pubsub.subscribe("bidding_updates")

async def listen_to_redis():
    """Listen for messages on Redis Pub/Sub."""
    while True:
        try:
            message = pubsub.get_message()
            if message and message["type"] == "message":
                auction_id, highest_bid = message["data"].split(":")
                print(f"New bid received: Auction ID {auction_id}, Highest Bid {highest_bid}")

                # Update Supabase with the new highest bid
                update_highest_bid_in_supabase(auction_id, highest_bid)

                # Broadcast update via WebSockets
                await broadcast_to_clients(auction_id, highest_bid)
        except Exception as e:
            print(f"Error in Redis listener: {e}")
        await asyncio.sleep(0.01)  # Avoid busy waiting


def update_highest_bid_in_supabase(auction_id, highest_bid):
    """Update the highest bid in Supabase."""
    try:
        supabase.table('marketplace').update({
            'highest_bid': highest_bid
        }).eq('auction_id', auction_id).execute()
    except Exception as e:
        print(f"Error updating Supabase: {e}")

#################################################################################################################

@app.route('/')
def home():
    return "Marketplace API is running!"

# Health check for websocket
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "Marketplace API is running!"}), 200


# Create a new listing
@app.route('/api/marketplace/listings', methods=['POST'])
def create_listing():
    try:
        # Check if there's an image file in the request
        image_file = None
        if 'image' in request.files:
            image_file = request.files['image']

        # Get JSON data from form
        listing_data = json.loads(request.form.get('data', '{}'))

        # Validate required fields
        required_fields = ['seller_id', 'card_id', 'title', 'price', 'type']
        for field in required_fields:
            if field not in listing_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Additional validation for auction type
        if listing_data.get('type') == 'auction':
            if 'auction_start_date' not in listing_data or 'auction_end_date' not in listing_data:
                return jsonify({"error": "Auction listings require start and end dates"}), 400

        # Validate seller_id is a valid UUID
        try:
            if 'seller_id' in listing_data:
                uuid_obj = uuid.UUID(listing_data['seller_id'])
        except ValueError:
            return jsonify({"error": "Invalid seller_id format, must be UUID"}), 400

        # Handle image upload if present
        if image_file and image_file.filename != '':
            # Generate a unique filename
            filename = f"{uuid.uuid4()}-{secure_filename(image_file.filename)}"
            file_path = f"listings/{filename}"
            bucket_name = "marketplace-images"

            # Read file content
            file_content = image_file.read()

            # Upload to Supabase storage
            supabase.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": image_file.content_type}
            )

            # Get the public URL
            image_url = supabase.storage.from_(bucket_name).get_public_url(file_path)

            # Add the image URL to the listing data
            listing_data['image_url'] = image_url

        # Insert the listing into Supabase
        result = supabase.table('marketplace').insert(listing_data).execute()
        new_listing_id = result.data[0]['id']

        if listing_data.get('type') == 'auction':
            redis_client.set(new_listing_id, listing_data['price'])

        return jsonify(result.data[0]), 201

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Print the full stack trace
        return jsonify({"error": str(e)}), 500

# Get all listings
@app.route('/api/marketplace/listings', methods=['GET'])
def get_listings():
    try:
        # Get query parameters for filtering
        status = request.args.get('status', 'active')
        type_filter = request.args.get('type')
        seller_id = request.args.get('seller_id')
        card_id = request.args.get('card_id')

        # Build the query
        query = supabase.table('marketplace').select('*')

        # Apply filters if provided
        if status:
            query = query.eq('status', status)
        if type_filter:
            query = query.eq('type', type_filter)
        if seller_id:
            query = query.eq('seller_id', seller_id)
        if card_id:  # Add this condition to filter by card_id
            query = query.eq('card_id', card_id)

        # Execute the query
        result = query.execute()

        return jsonify(result.data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get a specific listing by ID
@app.route('/api/marketplace/listings/<listing_id>', methods=['GET'])
def get_listing(listing_id):
    try:
        # Validate UUID format
        try:
            uuid_obj = uuid.UUID(listing_id)
        except ValueError:
            return jsonify({"error": "Invalid listing ID format"}), 400

        # Query the listing
        result = supabase.table('marketplace').select('*').eq('id', listing_id).execute()

        if not result.data:
            return jsonify({"error": "Listing not found"}), 404

        # Return the listing directly
        return jsonify(result.data[0]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update a listing
@app.route('/api/marketplace/listings/<listing_id>', methods=['PUT'])
def update_listing(listing_id):
    try:
        data = request.json

        # Validate UUID format
        try:
            uuid_obj = uuid.UUID(listing_id)
        except ValueError:
            return jsonify({"error": "Invalid listing ID format"}), 400

        # Check if listing exists
        check_result = supabase.table('marketplace').select('id, type').eq('id', listing_id).execute()

        if not check_result.data:
            return jsonify({"error": "Listing not found"}), 404

        # Additional validation for auction type
        if data.get('type') == 'auction':
            if 'auction_start_date' not in data and 'auction_end_date' not in data:
                current_type = check_result.data[0].get('type')
                if current_type != 'auction':
                    return jsonify({"error": "Auction listings require start and end dates"}), 400

        # Validate seller_id is a valid UUID if provided
        try:
            if 'seller_id' in data:
                uuid_obj = uuid.UUID(data['seller_id'])
            if 'highest_bidder_id' in data:
                uuid_obj = uuid.UUID(data['highest_bidder_id'])
        except ValueError:
            return jsonify({"error": "Invalid UUID format for seller_id or highest_bidder_id"}), 400

        # Update the listing
        result = supabase.table('marketplace').update(data).eq('id', listing_id).execute()

        return jsonify(result.data[0]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete a listing
@app.route('/api/marketplace/listings/<listing_id>', methods=['DELETE'])
def delete_listing(listing_id):
    try:
        # Validate UUID format
        try:
            uuid_obj = uuid.UUID(listing_id)
        except ValueError:
            return jsonify({"error": "Invalid listing ID format"}), 400

        # Check if listing exists
        check_result = supabase.table('marketplace').select('id').eq('id', listing_id).execute()

        if not check_result.data:
            return jsonify({"error": "Listing not found"}), 404

        # Delete the listing
        result = supabase.table('marketplace').delete().eq('id', listing_id).execute()

        return jsonify({"message": "Listing deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get multiple listings by passing an array of IDs
@app.route('/api/marketplace/listings/batch', methods=['POST'])
def get_listings_batch():
    try:
        data = request.json
        listing_ids = data.get('listing_ids', [])

        # Validate input
        if not listing_ids or not isinstance(listing_ids, list):
            return jsonify({"error": "A list of listing_ids is required"}), 400

        # Validate each ID is a valid UUID
        for listing_id in listing_ids:
            try:
                uuid_obj = uuid.UUID(listing_id)
            except ValueError:
                return jsonify({"error": f"Invalid listing ID format: {listing_id}"}), 400

        # Query the listings - Supabase doesn't have a direct "in" filter,
        # so we'll use a more complex approach with "or" filters
        if not listing_ids:
            return jsonify([]), 200

        # Build the query with OR conditions
        query = supabase.table('marketplace').select('*')

        # For the first ID we start the filter chain
        query = query.eq('id', listing_ids[0])

        # For all other IDs we add OR conditions
        for listing_id in listing_ids[1:]:
            query = query.or_(f'id.eq.{listing_id}')

        # Execute the query
        result = query.execute()

        return jsonify(result.data), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
