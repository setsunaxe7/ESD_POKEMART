from flask import Flask, request, jsonify
import logging
import requests  # For HTTP calls
import pika
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Config for Inventory Microservice
INVENTORY_URL = "http://localhost:5003/inventory/update"  # You may need to adjust the host

# Simulated payment URL (replace with actual)
PAYMENT_URL = "http://localhost:5002/refund"

# Endpoint to receive inspection results
@app.route('/update-inspection-result', methods=['POST'])
def update_inspection_result():
    try:
        data = request.json
        request_id = data.get('requestId')
        inspection_result = data.get('inspectionResult')
        user_id = data.get('userId')
        order_id = data.get('orderId')
        card_id = data.get('cardId')

        if not all([request_id, inspection_result, user_id, order_id, card_id]):
            return jsonify({'error': 'Missing required fields'}), 400

        logging.info(f"Received inspection result for request {request_id}: {inspection_result}")

        if inspection_result == 'damaged':
            # ✅ Refund Phase
            logging.info("Initiating refund process...")

            refund_payload = {
                'userId': user_id,
                'orderId': order_id,
                'cardId': card_id
            }

            payment_response = requests.post(PAYMENT_URL, json=refund_payload)

            if payment_response.status_code == 200:
                logging.info("Refund successful, updating inventory...")

                inventory_payload = {
                    'cardId': card_id
                }

                inventory_response = requests.post(INVENTORY_URL, json=inventory_payload)

                if inventory_response.status_code == 200:
                    logging.info("Inventory updated successfully.")
                else:
                    logging.warning(f"Failed to update inventory: {inventory_response.text}")

            else:
                logging.warning(f"Refund failed: {payment_response.text}")

        elif inspection_result == 'good condition':
            # ❌ Reject refund
            logging.info("Refund request rejected: Card is in good condition.")

        return jsonify({
            'message': 'Inspection result processed successfully.',
            'requestId': request_id,
            'inspectionResult': inspection_result
        }), 200

    except Exception as e:
        logging.error(f"Error in update_inspection_result: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
