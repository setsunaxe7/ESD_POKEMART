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
rabbit_host = "localhost"
rabbit_port = 5672
exchange_name = "grading_topic"
exchange_type = "topic"

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
@app.route("/grading/create_request", methods=["POST"])
def grade_card():
    if request.is_json:
        try:
            data = request.get_json()
            print("\nReceived grading request:", data)

            # Extract required fields
            cardID = data.get("cardID")
            address = data.get("address")
            postalCode = data.get("postalCode")

            if not all([cardID, address, postalCode]):
                return jsonify({"code": 400, "message": "Missing required fields"}), 400


            # Send to Grader 
            result = sendGradingAndNotify(cardID, address, postalCode)
            
            return jsonify(result), result["code"]

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = f"{str(e)} at {exc_type}: {fname}: line {exc_tb.tb_lineno}"
            print("Error:", ex_str)

            return jsonify({"code": 500, "message": "Internal error", "exception": ex_str}), 500

    return jsonify({"code": 400, "message": "Invalid JSON input"}), 400

# sendGradingAndNotify function send to external grader and inform user
def sendGradingAndNotify(cardID, address, postalCode):
    gradingMessage = json.dumps({
        "cardID": cardID,
        "address": address,
        "postalCode": postalCode
    })

    try:
        # Publish to RabbitMQ
        print("  Publishing grading request to RabbitMQ...")
        channel.basic_publish(
            exchange=exchange_name, routing_key="create.grader", body=gradingMessage
        )
    
        return {
            "code": 201,
            "status": "successful",
            # "data": {
            #     "gradingID": gradingID,
            #     "cardID": cardID,
            #     "cardStatus": cardStatus,
            #     "address": address,
            #     "postalCode": postalCode
            # }
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

# Run at start
if __name__ == "__main__":
    print("Starting Flask service for card grading...")
    connectAMQP()
    app.run(host="0.0.0.0", port=5100, debug=True)
