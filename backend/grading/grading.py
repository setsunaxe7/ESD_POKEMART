from flask import jsonify
from supabase import create_client
from dotenv import load_dotenv
import json
import sys, os
import uuid  
import amqp_lib

# Supabase configuration
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key= os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# RabbitMQ Config
rabbit_host = "localhost"
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

# Creation function, comes from websocket/ui, takes in bkey create.grading EXACT
def grade_card(channel, method, properties, body):
    result = json.loads(body)
    try:
        print("\nReceived grading request:", result)

        # Extract required fields
        cardID = result["cardID"]
        address = result["address"]
        postalCode = result["postalCode"]
        userID = result["userID"]

        if not all([cardID, address, postalCode]):
            return jsonify({"code": 400, "message": "Missing required fields"}), 400

        # Generate unique grading ID
        gradingID = str(uuid.uuid4())
        
        # init data for db
        data = {
            "userID": userID,
            "gradingID": gradingID,
            "cardID": cardID,
            "address": address,
            "status": "Created",
            "postalCode": postalCode, 
            "result": "", 
            
        }

        # Upload to Supabase storage
        response = supabase.table("grading").insert(data).execute()
        
        # if response.error is None:
        #     print("Data inserted successfully:", response.data)
        # else:
        #     print("Error inserting data:", response.error)
        
        # Default card status
        cardStatus = "Pending Grading"
        
        # Connection to AMQP
        if connection is None or not amqp_lib.is_connection_open(connection):
            connectAMQP()
        
        # Send to External Grader and Notify User
        result = sendGradingAndNotify(gradingID, cardID, cardStatus, address, postalCode)

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
            exchange=exchange_name, routing_key="create.externalGrading", body=gradingMessage
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
        
        

# takes in bkey get.grading EXACT
def getDB(channel, method, properties, body):
    result = json.loads(body)
    print("\nReceived grading request:", result)
    
    try:
        # print("\nReceived grading request:", result)
        # Parse UUID from body
        userID = result["userID"]
        if not userID:
            raise ValueError("Missing 'userID' in request body.")

        # Query Supabase table
        print(f"Querying Supabase for UserID: {userID}")
        response = supabase.table("grading").select("*").eq("userID", userID).execute()

        if response.data:
            payload = json.dumps(response.data)
        else:
            payload = json.dumps({"error": "No record found"})

        # Publish to RabbitMQ
        print("Publishing data to RabbitMQ...")
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=".return",
            body=payload
        )
    except Exception as e:
        error_payload = json.dumps({"error": str(e)})
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=".return",
            body=error_payload
        )

# Update function, takes in bkey .update
def update(channel, method, propertites, body):
    result = json.loads(body)
    print(f"Grader message (JSON): {result}")
    result_json = json.dumps(result)
    channel.basic_publish(
        exchange=exchange_name, routing_key="externalGrader.notify", body=result_json
    )

# incoming from externalGrader/ Delivery APIdef callback(channel, method, properties, body):
def callback(channel, method, properties, body):
    try:
        # Get the routing key
        routing_key = method.routing_key  

        # Log or print the routing key and message
        if routing_key == "create.grading":
            print(f"Received message with routing key: {routing_key}")
            grade_card(channel, method, properties, body)
        elif routing_key == "get.grading":
            print(f"Received message with routing key: {routing_key}")
            getDB(channel, method, properties, body)
        elif ".update" in routing_key:
            print(f"Received message with routing key: {routing_key}")
            update(channel, method, properties, body)

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
