from flask import Flask, request, jsonify
import logging

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Endpoint to receive inspection results
@app.route('/update-inspection-result', methods=['POST'])
def update_inspection_result():
    try:
        data = request.json
        request_id = data.get('requestId')
        inspection_result = data.get('inspectionResult')

        if not request_id or not inspection_result:
            return jsonify({'error': 'Missing required fields (requestId, inspectionResult)'}), 400

        # Process the inspection result (e.g., update the refund status)
        logging.info(f"Received inspection result for request {request_id}: {inspection_result}")

        # Simulate processing the result
        if inspection_result == 'damaged':
            # Initiate refund process
            logging.info("Initiating refund process...")
        elif inspection_result == 'good condition':
            # Reject refund request
            logging.info("Refund request rejected: Card is in good condition.")

        return jsonify({
            'message': 'Inspection result processed successfully.',
            'requestId': request_id,
            'inspectionResult': inspection_result
        }), 200
    except Exception as e:
        logging.error(f"Error in update_inspection_result: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Start the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)