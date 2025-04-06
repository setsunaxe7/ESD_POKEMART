from flask import Flask, request, jsonify 
from flask_cors import CORS
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Supabase configuration
supabase_url = os.getenv("SUPABASE_URL")
supabase_key= os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

@app.route('/')
def home():
    return "Card Collection API"

# Get all cards from inventory
@app.route('/inventory', methods=['GET'])
def get_cards():
    response = supabase.table('cards').select('*').execute()
    return jsonify(response.data)

# Get a specific card by card_id
@app.route('/inventory/<card_id>', methods=['GET'])
def get_card(card_id):
    response = supabase.table('cards').select('*').eq('id', card_id).execute()
    return jsonify(response.data[0])

@app.route('/inventory/update', methods=['POST'])
def update_inventory():
    data = request.json
    card_id = data.get('cardId')

    if not card_id:
        return jsonify({'error': 'Missing cardId'}), 400
    if card_id:
        return jsonify({'message':'Inventory reached'}),200

    # You could adjust the logic here — for example, mark the card as available again
    # response = supabase.table('cards').update({'status': 'refunded'}).eq('id', card_id).execute()

    # if response.data:
    #     return jsonify({'message': 'Inventory updated successfully', 'cardId': card_id}), 200
    # else:
    #     return jsonify({'error': 'Failed to update inventory'}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
