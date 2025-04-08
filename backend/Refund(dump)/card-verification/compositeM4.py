from flask import Flask, request, jsonify
from datetime import datetime
import logging
import requests
import pika
import json

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Config for other microservices
PAYMENT_URL = "http://localhost:8000/payment/refund"
NOTIFICATION_URL = "https://personal-gvra7qzz.outsystemscloud.com/Notification/rest/NotificationAPI/api/notification/receive"

# RabbitMQ config
exchange_name = "refund_topic"
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
            properties=pika.BasicProperties(delivery_mode=2)
        )
        logging.info("Notification published to RabbitMQ.")
        connection.close()
    except Exception as e:
        logging.error(f"Failed to publish to RabbitMQ: {e}")

# Call OutSystems Notification API
def send_external_notification(notification_data):
    try:
        response = requests.post(NOTIFICATION_URL, json={
            "Service": notification_data["Service"],
            "Text": "",
            "Timestamp": notification_data["TimeStamp"],
            "Data": {
                "UserID": notification_data.get("UserID", ""),
                "CardID": notification_data["CardID"],
                "Status": notification_data["Status"],
                "GradingID": "",
                "ShippingID": "",
                "PickupDate": "",
                "AuctionID": "",
                "Price": "",
                "PhoneNumber": "+6598895901"
            }
        })

        if response.status_code == 200:
            logging.info("Successfully sent notification to OutSystems.")
        else:
            logging.warning(f"OutSystems notification failed: {response.status_code} - {response.text}")

    except Exception as e:
        logging.error(f"Error sending notification to OutSystems: {e}")
@app.route('/refund-process', methods=['POST'])
def start_refund_process():
    try:
        # Log the incoming request data from UI for inspection
        logging.info(f"Received refund request payload: {request.get_json()}")

        data = request.get_json()

        required_fields = ['cardId', 'transactionId', 'imageUrl', 'userId', 'refundReason']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

        # Optional field
        details = data.get('details', '')

        # Prepare payload for verification microservice
        payload = {
            'cardId': data['cardId'],
            'transactionId': data['transactionId'],
            'imageUrl': data['imageUrl'],
            'refundReason': data['refundReason'],
            'userId': data['userId'],
            'details': details
        }

        # Forward to card verification microservice
        response = requests.post("http://localhost:3000/verify", json=payload)

        if response.status_code == 200:
            logging.info("Successfully forwarded refund request to card verification.")
            return jsonify({'message': 'Refund request forwarded successfully'}), 200
        else:
            logging.warning(f"Card verification service responded with {response.status_code}: {response.text}")
            return jsonify({'error': 'Card verification service failed', 'details': response.text}), 502

    except Exception as e:
        logging.error(f"Error in /refund-process: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
    
# Endpoint to receive inspection results
@app.route('/update-inspection-result', methods=['POST'])
def update_inspection_result():
    try:
        data = request.json
        request_id = data.get('requestId')
        inspection_result = data.get('inspectionResult')
        user_id = data.get('userId')
        card_id = data.get('cardId')
        transaction_id = data.get('transactionId')

        if not all([request_id, inspection_result, user_id, transaction_id, card_id]):
            return jsonify({'error': 'Missing required fields'}), 400

        logging.info(f"Received inspection result for request {request_id}: {inspection_result}")

        if inspection_result == 'Refund':
            logging.info("Initiating refund process...")

            refund_payload = {
                'userId': user_id,
                'transactionId': transaction_id,
                'cardId': card_id
            }

            payment_response = requests.post(PAYMENT_URL, json=refund_payload)

            if payment_response.status_code == 200:
                logging.info("Refund successful, notifying user")

                notification = {
                    "Service": "Refund",
                    "CardID": card_id,
                    "Status": "Refund Successful",
                    "TimeStamp": datetime.now().isoformat()
                }
                publish_notification(notification)
                send_external_notification(notification)

            else:
                logging.warning(f"Refund failed: {payment_response.text}")
                notification = {
                    "Service": "Refund",
                    "CardID": card_id,
                    "Status": "Refund Failed",
                    "TimeStamp": datetime.now().isoformat()
                }
                publish_notification(notification)
                send_external_notification(notification)

        elif inspection_result == 'Reject':
            logging.info("Refund request rejected: Card is in good condition.")
            notification = {
                "Service": "Refund",
                "CardID": card_id,
                "Status": "Refund Rejected",
                "TimeStamp": datetime.now().isoformat()
            }
            publish_notification(notification)
            send_external_notification(notification)

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


