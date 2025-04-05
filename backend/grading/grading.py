from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pika
import sys, os
import uuid  # To generate unique grading IDs

import amqp_lib

app = Flask(__name__)
CORS(app)

# RabbitMQ Config
rabbit_host = "rabbitmq"
rabbit_port = 5672
exchange_name = "grading_topic"
exchange_type = "topic"
queue_name = "grading"

connection = None
channel = None

def connectAMQP():
    global connection, channel
    print("  Connecting to AMQP broker...")
    try:
        connection, channel = amqp_lib.connect(
            hostname=rabbit_host,
            port=rabbit_port,
            exchange_name=exchange_name,
            exchange_type=exchange_type,
        )
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
        exit(1)

# Creation function 
# Suppose to take in bKey .create
# comes from websocket/ui

def grade_card(channel, method, properties, body):
    result = json.loads(body)
    try:
        print("\nReceived grading request:", result)

        # Extract required fields
        cardID = result["cardID"]
        address = result["address"]
        postalCode = result["postalCode"]

        if not all([cardID, address, postalCode]):
            return jsonify({"code": 400, "message": "Missing required fields"}), 400

        # Generate unique grading ID
        gradingID = str(uuid.uuid4())

        # Default card status
        cardStatus = "Pending Grading"
        
        # Connection to AMQP
        if connection is None or not amqp_lib.is_connection_open(connection):
            connectAMQP()
        
        # Send to External Grader and Notify User
        result = sendGradingAndNotify(gradingID, cardID, cardStatus, address, postalCode)

        # Manually push Flask context
        with app.app_context():
            return jsonify(result), result["code"]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = f"{str(e)} at {exc_type}: {fname}: line {exc_tb.tb_lineno}"
        print("Error:", ex_str)

        return jsonify({"code": 500, "message": "Internal error", "exception": ex_str}), 500

# sendGradingAndNotify function send to external grader and inform user
def sendGradingAndNotify(gradingID, cardID, cardStatus, address, postalCode):
    gradingMessage = json.dumps({
        "gradingID": gradingID,
        "cardID": cardID,
        "cardStatus": cardStatus,
        "address": address,
        "postalCode": postalCode
    })

    try:
        # Publish to RabbitMQ
        print("  Publishing grading request to RabbitMQ...")
        channel.basic_publish(
            exchange=exchange_name, routing_key="create.externalGrader", body=gradingMessage
        )
        
        notificationMessage = json.dumps({
                "gradingID": gradingID,
                "cardID": cardID,
                "cardStatus": cardStatus,
            })

        print("  Publishing notification request to RabbitMQ...")
        channel.basic_publish(
            exchange=exchange_name, routing_key="creation.notify", body=notificationMessage
        )

        return {
            "code": 201,
            "status": "successful",
            "gradingId": gradingID
        }
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = f"{str(e)} at {exc_type}: {fname}: line {exc_tb.tb_lineno}"
        return {
            "code": 500,
            "message": "Internal error",
            "exception": ex_str
        }

# Update function 
# Suppose to take in bKey .update
# incoming from externalGrader/ Delivery APIdef callback(channel, method, properties, body):
def callback(channel, method, properties, body):
    try:
        result = json.loads(body)
        routing_key = method.routing_key  # Get the routing key

        # Log or print the routing key and message
        if "grader" in routing_key:
            grade_card(channel, method, properties, body)
        else:
            print(f"Received message with routing key: {routing_key}")
            print(f"Grader message (JSON): {result}")
            result_json = json.dumps(result)
            channel.basic_publish(
                exchange=exchange_name, routing_key="externalGrader.notify", body=result_json
            )
    except Exception as e:
        print(f"Unable to parse JSON: {e=}")
        print(f"Grader message: {body}")

# Run at start
if __name__ == "__main__":
    print(f"This is {os.path.basename(__file__)} - amqp consumer...")
    try:
        amqp_lib.start_consuming(
            rabbit_host, rabbit_port, exchange_name, exchange_type, queue_name, callback
        )
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
