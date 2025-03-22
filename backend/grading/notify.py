#!/usr/bin/env python3
import os
import amqp_lib
import json

rabbit_host = "localhost"
rabbit_port = 5672
exchange_name = "grading_topic"
exchange_type = "topic"
queue_name = "notification"


def callback(channel, method, properties, body):
    # required signature for the callback; no return
    try:
        result = json.loads(body)
        print(f"Notification message (JSON): {result}")
    except Exception as e:
        print(f"Unable to parse JSON: {e=}")
        print(f"Notification message: {body}")
    print()


# here suppose to shoot out to ui thru websocket but notification done by outsystem

if __name__ == "__main__":
    print(f"This is {os.path.basename(__file__)} - amqp consumer...")
    try:
        amqp_lib.start_consuming(
            rabbit_host, rabbit_port, exchange_name, exchange_type, queue_name, callback
        )
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
