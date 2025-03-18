from flask import Flask, request, jsonify
from supabase import create_client
import requests

app = Flask(__name__)

# Supabase configuration
supabase_url = 'https://wibdppsuolkiwqurhlya.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndpYmRwcHN1b2xraXdxdXJobHlhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIwNDMwMDYsImV4cCI6MjA1NzYxOTAwNn0.0RtuBXAX2QYBUoXu7-ay9Uhs7mJzVTL45OzjFoVHoDE'
supabase = create_client(supabase_url, supabase_key)

# Create a table in Supabase called 'cards' with appropriate columns
# such as id, name, image_url, set_id, etc.

@app.route('/')
def home():
    return "Card Collection API"

@app.route('/fetch-cards', methods=['POST'])
def fetch_and_store_cards():
    # Example: Fetch Pokémon cards from an external API
    set_id = request.json.get('set_id', 'sv3')  # Default to Scarlet & Violet 151

    # Make request to external API
    external_api_url = f'https://api.pokemontcg.io/v2/cards?q=set.id:{set_id}'
    headers = {'X-Api-Key': '1bdbe362-1c4f-47bf-9f67-c5553234c826'}

    response = requests.get(external_api_url, headers=headers)
    cards_data = response.json()['data']

    # Process and store each card in Supabase
    for card in cards_data:
        card_entry = {
            'name': card['name'],
            'image_url': card['images']['small'],
            'high_res_image': card['images']['large'],
            'set_id': set_id,
            'rarity': card.get('rarity', ''),
            'card_id': card['id'],
            # Add any other fields you want to store
        }

        supabase.table('cards').insert(card_entry).execute()

    return jsonify({'message': f'Successfully imported {len(cards_data)} cards'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
