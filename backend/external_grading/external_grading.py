#!/usr/bin/env python3
import os
import amqp_lib
import json
from dotenv import load_dotenv
from supabase import create_client
import random

rabbit_host = "rabbitmq"
rabbit_port = 5672
exchange_name = "grading_topic"
exchange_type = "topic"
queue_name = "external_grading"

connection = None
channel = None

# Supabase configuration
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key= os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

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

def update_status(channel, method, properties, body):
    try:
        result = json.loads(body)
        result["status"] = "In Progress"
        result_json = json.dumps(result)
        
        if connection is None or not amqp_lib.is_connection_open(connection):
            connectAMQP()
        
        channel.basic_publish(
            exchange=exchange_name, routing_key="status.update", body=result_json
        )  
        
        # db
        response = supabase.table("external_grading").insert(result).execute()
        
        if response.data:
            print("Data inserted successfully:", response.data)
        else:
            print("Error inserting data:", response.error)
        
        print(f"External Grader message (JSON): {result_json}")
    except Exception as e:
        print(f"Unable to parse JSON: {e=}")
        print(f"External Grader message: {body}")
    print()
    
def get_result(channel, method, properties, body):
    try:
        print(body)
        result = json.loads(body)
        print(result)
        response = supabase.table("external_grading").select("*").eq("gradingID", result["gradingID"]).execute()
        response_data = response.data[0] 
        response_data["status"] = "Graded"
        
        grade = random.randint(1, 10)
        response_data["result"] = "PSA " + str(grade)
        
        result_json = json.dumps(response_data)
        
        if connection is None or not amqp_lib.is_connection_open(connection):
            connectAMQP()
        
        channel.basic_publish(
            exchange=exchange_name, routing_key="result.update", body=result_json
        )  
        
        print(f"External Grader message (JSON): {result_json}")
    except Exception as e:
        print(f"Unable to parse JSON: {e=}")
        print(f"External Grader message: {body}")
    print()    

def callback(channel, method, properties, body):
    # required signature for the callback; no return
    routing_key = method.routing_key  
    
    if routing_key == "create.externalGrading":
        print(f"Received message with routing key: {routing_key}")
        update_status(channel, method, properties, body)
    elif routing_key == "update.externalGrading":
        print(f"Received message with routing key: {routing_key}")
        get_result(channel, method, properties, body)


if __name__ == "__main__":
    print(f"This is {os.path.basename(__file__)} - amqp consumer...")
    try:
        amqp_lib.start_consuming(
            rabbit_host, rabbit_port, exchange_name, exchange_type, queue_name, callback
        )
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
