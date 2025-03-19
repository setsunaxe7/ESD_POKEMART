from flask import Flask, jsonify
from flask_cors import CORS
from supabase import create_client

app = Flask(__name__)
CORS(app)

# Supabase configuration
supabase_url = 'https://wibdppsuolkiwqurhlya.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndpYmRwcHN1b2xraXdxdXJobHlhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIwNDMwMDYsImV4cCI6MjA1NzYxOTAwNn0.0RtuBXAX2QYBUoXu7-ay9Uhs7mJzVTL45OzjFoVHoDE'
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
    response = supabase.table('cards').select('*').eq('card_id', card_id).execute()
    return jsonify(response.data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
