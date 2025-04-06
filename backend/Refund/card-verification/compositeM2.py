from flask import Flask, request, jsonify
import logging
import requests
import pika
import json

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Config for other microservices
INVENTORY_URL = "http://localhost:5003/inventory/update"
PAYMENT_URL = "http://localhost:5002/refund"

# RabbitMQ config
exchange_name = "grading_topic"
routing_key = "refund.notify"

# Set up RabbitMQ connection
def publish_notification(message):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)

        channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
        )
        logging.info("Notification published to RabbitMQ.")
        connection.close()
    except Exception as e:
        logging.error(f"Failed to publish to RabbitMQ: {e}")

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

                inventory_payload = {'cardId': card_id}
                inventory_response = requests.post(INVENTORY_URL, json=inventory_payload)

                if inventory_response.status_code == 200:
                    logging.info("Inventory updated successfully.")

                # ✅ Notify user
                notification = {
                    "userId": user_id,
                    "orderId": order_id,
                    "cardId": card_id,
                    "status": "Refund Successful"
                }
                publish_notification(notification)

            else:
                logging.warning(f"Refund failed: {payment_response.text}")
                publish_notification({
                    "userId": user_id,
                    "orderId": order_id,
                    "cardId": card_id,
                    "status": "Refund Failed"
                })

        elif inspection_result == 'good condition':
            logging.info("Refund request rejected: Card is in good condition.")
            publish_notification({
                "userId": user_id,
                "orderId": order_id,
                "cardId": card_id,
                "status": "Refund Cancelled: Card in Good Condition"
            })

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

