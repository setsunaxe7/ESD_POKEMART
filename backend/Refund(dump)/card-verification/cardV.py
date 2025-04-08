from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from datetime import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import logging
import uuid
import requests
import os


load_dotenv()

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

# Supabase Setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Submit verification request with photo upload
@app.route('/verify', methods=['POST'])
def submit_verification_request():
    try:
        card_id = request.form.get('cardId')
        transaction_id = request.form.get('transactionId')
        user_id = request.form.get('userId')
        refund_reason = request.form.get('refundReason')
        details = request.form.get('details')

        photo = request.files.get('image')
        if not all([card_id, transaction_id, user_id, refund_reason, photo]):
            return jsonify({'error': 'Missing required fields'}), 400



        # Handle image upload if present
        if photo and photo.filename != '':
            # Generate a unique filename
            filename = f"{uuid.uuid4()}-{secure_filename(photo.filename)}"
            file_path = f"refund/{filename}"
            bucket_name = "refund-photos"

            # Read file content
            file_content = photo.read()

            # Upload to Supabase storage
            supabase.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": photo.content_type}
            )

            # Get the public URL
            image_url = supabase.storage.from_(bucket_name).get_public_url(file_path)

        # Save record in Supabase DB
        record = {
            'cardId': card_id,
            'userId': user_id,
            'transactionId': transaction_id,
            'refundReason': refund_reason,
            'details': details,
            'status': 'pending',
            'timestamp': datetime.utcnow().isoformat(),
            'imageUrl': image_url  # save the image URL in your table too
        }
        supabase.table('verification_requests').insert(record).execute()

        return jsonify({'message': 'Verification request submitted successfully'}), 200

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
    app.run(host='0.0.0.0', port=3005)
