from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import logging

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Firebase
try:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    logging.error(f"Firebase initialization failed: {e}")

# Endpoint for Person A to submit a verification request
@app.route('/verify', methods=['POST'])
def submit_verification_request():
    try:
        data = request.json
        card_id = data.get('cardId')
        order_id = data.get('orderId')
        photo_url = data.get('photoUrl')

        if not card_id or not order_id or not photo_url:
            return jsonify({'error': 'Missing required fields (cardId, orderId, photoUrl)'}), 400

        # Store the verification request in Firestore
        verification_request = {
            'cardId': card_id,
            'orderId': order_id,
            'photoUrl': photo_url,
            'status': 'pending',  # Initial status
            'timestamp': datetime.now().isoformat()
        }
        request_ref = db.collection('verification_requests').add(verification_request)

        # Notify Person A that the verification is in progress
        return jsonify({
            'message': 'Verification request received. Inspection is in progress.',
            'requestId': request_ref[1].id  # Return the Firestore document ID
        }), 200
    except Exception as e:
        logging.error(f"Error in submit_verification_request: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Endpoint for Person B to update the inspection result
@app.route('/update-result', methods=['POST'])
def update_inspection_result():
    try:
        data = request.json
        request_id = data.get('requestId')
        inspection_result = data.get('inspectionResult')

        if not request_id or not inspection_result:
            return jsonify({'error': 'Missing required fields (requestId, inspectionResult)'}), 400

        # Update the verification request in Firestore
        request_ref = db.collection('verification_requests').document(request_id)
        request_ref.update({
            'status': 'completed',
            'inspectionResult': inspection_result,
            'updatedAt': datetime.now().isoformat()
        })

        # Notify Person A of the result (simulate notification)
        notify_person_a(request_id, inspection_result)

        return jsonify({
            'message': 'Inspection result updated successfully.',
            'requestId': request_id,
            'inspectionResult': inspection_result
        }), 200
    except Exception as e:
        logging.error(f"Error in update_inspection_result: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Simulate notifying Person A
def notify_person_a(request_id, inspection_result):
    # In a real scenario, this could send an email, SMS, or push notification
    logging.info(f"Notifying Person A: Request {request_id} has been updated with result: {inspection_result}")

# Start the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)