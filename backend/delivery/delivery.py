#!/usr/bin/env python3
from dotenv import load_dotenv
import json
import os
import amqp_lib
import requests

rabbit_host = "rabbitmq"
rabbit_port = 5672
exchange_name = "grading_topic"
exchange_type = "topic"
queue_name = "delivery"

connection = None
channel = None

load_dotenv()
delivery_api_key = os.getenv("DELIVERY_API_KEY")

# RabbitMQ Connector
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

def callback(channel, method, properties, body):
    # required signature for the callback; no return
    try:
        result = json.loads(body)
        url = 'https://personal-slqn7xxm.outsystemscloud.com/ESDProject_VanNova_/rest/JohnnyAPI/order'
        
        # print(result)
        
        headers = {
            "X-Api-Key": delivery_api_key,
            "X-User-Id": result["userID"],
            "Content-Type": "application/json"
        }
        
        if '#' in result["address"]:
            address_line1, address_line2 = result["address"].split("#")
            address_line2 = "#" + address_line2
        else:
            address_line1 = result["address"]
            address_line2 = ""
            
        data = {
            "order": {
                "orderDetails": str(result["gradingID"]),
                "fromAddressLine1": address_line1,
                "fromAddressLine2": address_line2,
                "fromZipCode": str(result["postalCode"]),
                "toAddressLine1": "90 Stamford Rd",
                "toAddressLine2": "#03-01",
                "toZipCode": "178903",
                "userId": str(result["userID"])
            }
        }

        response = requests.post(url, headers=headers, json=data)

        print("Status Code:", response.status_code)
        print("Response Body:", response.json())
        
        if connection is None or not amqp_lib.is_connection_open(connection):
            connectAMQP()
        
        
        result["deliveryID"] = response.json()["order"]["id"]
        result_json = json.dumps(result)
        
        channel.basic_publish(
            exchange=exchange_name, routing_key="delivery.update", body=result_json
        )  
        
        # print(f"Delivery Message (JSON): {response}")
    except Exception as e:
        print(f"Unable to parse JSON: {e=}")
        print(f"Delivery Message (JSON): {body}")
    print()


if __name__ == "__main__":
    print(f"This is {os.path.basename(__file__)} - amqp consumer...")
    try:
        amqp_lib.start_consuming(
            rabbit_host, rabbit_port, exchange_name, exchange_type, queue_name, callback
        )
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
