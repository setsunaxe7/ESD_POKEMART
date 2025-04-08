from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import logging
import requests

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
        transaction_id = data.get('transactionId')
        image_url = data.get('imageUrl')
        reason = data.get('refundReason')
        details = data.get('details')
        user_id = data.get('userId')

        required_fields = ['cardId', 'transactionId', 'imageUrl', 'userId', 'refundReason']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400


        # Store the verification request in Firestore
        verification_request = {
            'cardId': card_id,
            'userId': user_id,
            'transactionId': transaction_id,
            'imageUrl': image_url,
            'refundReason': reason,
            'details': details,
            'status': 'pending',  # Initial status
            'timestamp': datetime.now().isoformat()
        }
        request_ref = db.collection('verification_requests').add(verification_request)

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
        user_id = data.get('userId')
        card_id = data.get('cardId')
        transaction_id = data.get('transactionId')

        if not request_id or not inspection_result:
            return jsonify({'error': 'Missing required fields (requestId, inspectionResult)'}), 400

        # Update the verification request in Firestore
        request_ref = db.collection('verification_requests').document(request_id)
        request_ref.update({
            'status': 'completed',
            'inspectionResult': inspection_result,
            'updatedAt': datetime.now().isoformat()
        })

        # =============================================
        # Key Update: Immediately forward to Refund Microservice
        # =============================================
        refund_service_url = 'http://localhost:5000/update-inspection-result'  # Update if different
        payload = {
            'requestId': request_id,
            'inspectionResult': inspection_result,
            'userId': user_id,
            'cardId': card_id,
            'transactionId': transaction_id,
        }
        
        try:
            response = requests.post(refund_service_url, json=payload)
            if response.status_code == 200:
                logging.info(f"Successfully forwarded to Refund Service: {response.json()}")
            else:
                logging.error(f"Refund Service returned {response.status_code}: {response.text}")
                return jsonify({
                    'message': 'Inspection updated but failed to forward to Refund Service',
                    'error': response.text
                }), 500
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to connect to Refund Service: {e}")
            return jsonify({
                'message': 'Inspection updated but Refund Service unreachable',
                'error': str(e)
            }), 503
        # =============================================

        return jsonify({
            'message': 'Inspection result updated and forwarded to Refund Service',
            'requestId': request_id,
            'inspectionResult': inspection_result,
            'userId': user_id,
            'cardId': card_id,
            'transactionId': transaction_id,
            'refundServiceResponse': response.json() if response else None
        }), 200

    except Exception as e:
        logging.error(f"Error in update_inspection_result: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Start the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)