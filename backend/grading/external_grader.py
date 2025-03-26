#!/usr/bin/env python3
import os
import amqp_lib
import json

rabbit_host = "localhost"
rabbit_port = 5672
exchange_name = "grading_topic"
exchange_type = "topic"
queue_name = "external_grading"


def callback(channel, method, properties, body):
    # required signature for the callback; no return
    try:
        result = json.loads(body)
        result_pure = json.loads(body)
        # Convert result to a JSON string before publishing
        result["cardStatus"] = "received"
        result_json = json.dumps(result)
        
        channel.basic_publish(
            exchange=exchange_name, routing_key="externalGrader.update", body=result_json
        )
        print(f"External Grader message (JSON): {result_pure}")
    except Exception as e:
        print(f"Unable to parse JSON: {e=}")
        print(f"External Grader message: {body}")
    print()

if __name__ == "__main__":
    print(f"This is {os.path.basename(__file__)} - amqp consumer...")
    try:
        amqp_lib.start_consuming(
            rabbit_host, rabbit_port, exchange_name, exchange_type, queue_name, callback
        )
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
