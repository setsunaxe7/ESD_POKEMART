from flask import Flask, request, jsonify
from datetime import datetime
import logging
import requests
import pika
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Upload directory
# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Config for other microservices
PAYMENT_URL = "http://payment-service:5007/payment/refund"
NOTIFICATION_URL = "https://personal-gvra7qzz.outsystemscloud.com/Notification/rest/NotificationAPI/api/notification/receive"
CARD_VERIFICATION_URL = "http://verification-service:5010/CardVerification/verify"

# RabbitMQ config
exchange_name = "grading_topic"
routing_key = "*.notify"

# Set up RabbitMQ connection
def publish_notification(message):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672))
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
# def send_external_notification(notification_data):
#     try:
#         response = requests.post(NOTIFICATION_URL, json={
#             "Service": notification_data["Service"],
#             "Text": "",
#             "Timestamp": notification_data["TimeStamp"],
#             "Data": {
#                 "UserID": notification_data.get("UserID", ""),
#                 "CardID": notification_data["CardID"],
#                 "Status": notification_data["Status"],
#                 "GradingID": "",
#                 "ShippingID": "",
#                 "PickupDate": "",
#                 "AuctionID": "",
#                 "Price": "",
#                 "PhoneNumber": "+6598895901",
#                 "requestId": notification_data["requestId"]
#             }
#         })

#         if response.status_code == 200:
#             logging.info("Successfully sent notification to OutSystems.")
#         else:
#             logging.warning(f"OutSystems notification failed: {response.status_code} - {response.text}")

#     except Exception as e:
#         logging.error(f"Error sending notification to OutSystems: {e}")

@app.route('/refund-process', methods=['POST'])
def start_refund_process():
    try:
        # Forward form fields and file(s) as-is
        data = {key: request.form[key] for key in request.form}
        files = {
            key: (file.filename, file.stream, file.mimetype)
            for key, file in request.files.items()
        }

        # Send to card verification service
        response = requests.post(CARD_VERIFICATION_URL, data=data, files=files)

        return jsonify({'message': 'Forwarded successfully'}), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500





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
                'payment_intent_id': 'pi_3RBw4a2KPPVAucgy1G3KZmOI'
            }

            payment_response = requests.post(PAYMENT_URL, json=refund_payload)

            if payment_response.status_code == 200:
                logging.info("Refund successful, notifying user")
                status_msg = "Refund Successful"
            else:
                logging.warning(f"Refund failed: {payment_response.text}")
                status_msg = "Refund Failed"

        elif inspection_result == 'Reject':
            logging.info("Refund request rejected.")
            status_msg = "Refund Rejected"

        notification = {
            "Service": "Refund",
            "Text": '',
            "TimeStamp": datetime.now().isoformat(),
            "Data": {
                "CardID": card_id,
                "Status": status_msg,
                "UserID": user_id,
                "GradingID": "",
                "ShippingID": "",
                "AuctionID":"",
                "Price": "",
                "PhoneNumber": "+6598895901",
                "CardName" : "",
                "RefundID" : request_id

            }

        }

        publish_notification(notification)
        # send_external_notification(notification)

        return jsonify({
            'message': 'Inspection result processed successfully.',
            'requestId': request_id,
            'inspectionResult': inspection_result
        }), 200

    except Exception as e:
        logging.error(f"Error in update_inspection_result: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009)



