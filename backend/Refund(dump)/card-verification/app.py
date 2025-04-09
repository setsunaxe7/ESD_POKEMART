from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from datetime import datetime
import logging
import requests
import os

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

# Supabase Setup
SUPABASE_URL = "https://gixgfsneaxermosckfdl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpeGdmc25lYXhlcm1vc2NrZmRsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQwOTg1NDAsImV4cCI6MjA1OTY3NDU0MH0._mg4VE04PMfCIGuF7IVcVca-hZJjyGTdGaMbTP6EnwU"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Submit verification request with photo upload
@app.route('/verify', methods=['POST'])
def submit_verification_request():
    try:
        # multipart/form-data => use form and files
        card_id = request.form.get('cardId')
        transaction_id = request.form.get('transactionId')
        reason = request.form.get('refundReason')
        details = request.form.get('details')
        user_id = request.form.get('userId')
        photo = request.files.get('photo')

        # Validate required fields
        required_fields = [card_id, transaction_id, reason, user_id, photo]
        if not all(required_fields):
            return jsonify({'error': 'Missing one or more required fields.'}), 400

        # Upload photo to Supabase Storage
        filename = f"{user_id}_{datetime.utcnow().isoformat().replace(':', '-')}.jpg"
        file_path = f"card-photos/{filename}"

        upload_response = supabase.storage.from_('card-photos').upload(file_path, photo, {"content-type": "image/jpeg"})

        if upload_response.get('error'):
            return jsonify({'error': 'Failed to upload photo to Supabase Storage'}), 500

        # Get public URL
        public_url = supabase.storage.from_('card-photos').get_public_url(file_path)

        # Save to database
        record = {
            'cardId': card_id,
            'userId': user_id,
            'transactionId': transaction_id,
            'imageUrl': public_url,
            'refundReason': reason,
            'details': details,
            'status': 'pending',
            'timestamp': datetime.utcnow().isoformat()
        }

        insert_result = supabase.table("verification_requests").insert(record).execute()
        new_id = insert_result.data[0]['id']

        return jsonify({
            'message': 'Verification request received. Inspection in progress.',
            'requestId': new_id,
            'imageUrl': public_url
        }), 200

    except Exception as e:
        logging.error(f"Error in submit_verification_request: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500


# Update inspection result
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

        update_result = supabase.table("verification_requests").update({
            'status': 'completed',
            'inspectionResult': inspection_result,
            'updatedAt': datetime.utcnow().isoformat()
        }).eq("id", request_id).execute()

        # Forward to Refund Service
        refund_service_url = 'http://localhost:5000/update-inspection-result'
        payload = {
            'requestId': request_id,
            'inspectionResult': inspection_result,
            'userId': user_id,
            'cardId': card_id,
            'transactionId': transaction_id,
        }
        response = requests.post(refund_service_url, json=payload)

        return jsonify({
            'message': 'Inspection result updated and forwarded to Refund Service',
            'refundServiceResponse': response.json() if response else None
        }), 200

    except Exception as e:
        logging.error(f"Error in update_inspection_result: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
