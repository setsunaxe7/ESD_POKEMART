from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate('serviceAccountKey.json')  # Replace with your Firebase service account key
firebase_admin.initialize_app(cred)
db = firestore.client()

# Card verification endpoint
@app.route('/verify', methods=['POST'])
def verify_card():
    data = request.json
    card_id = data.get('cardId')
    order_id = data.get('orderId')
    photo = data.get('photo')

    if not card_id or not order_id or not photo:
        return jsonify({'error': 'Missing required fields (cardId, orderId, photo)'}), 400

    # Simulate manual verification (replace with actual manual process)
    print(f'Performing manual verification for card: {card_id}')
    inspection_result = perform_manual_verification(photo)  # Simulate manual verification
    timestamp = datetime.now().isoformat()

    # Store result in Firestore
    verification_result = {
        'cardId': card_id,
        'orderId': order_id,
        'inspectionResult': inspection_result,
        'timestamp': timestamp
    }
    db.collection('inspections').add(verification_result)

    # Return the result
    return jsonify(verification_result), 200

# Simulate manual verification
def perform_manual_verification(photo):
    # Simulate a manual verification process (e.g., a human inspects the photo)
    # For now, we'll randomly return "good condition" or "damaged"
    import random
    return 'good condition' if random.random() > 0.5 else 'damaged'

# Start the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)