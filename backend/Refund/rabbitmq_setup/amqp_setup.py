#!/usr/bin/env python3

"""
A standalone script to create exchanges and queues on RabbitMQ.
"""

import pika

# RabbitMQ connection details
amqp_host = "localhost"  # Use "rabbitmq" if running inside Docker
amqp_port = 5672
amqp_user = "guest"     # Default RabbitMQ username
amqp_password = "guest" # Default RabbitMQ password

exchange_name = "refund_topic"
exchange_type = "topic"

# Creates the exchange
def create_exchange(hostname, port, username, password, exchange_name, exchange_type):
    print(f"Connecting to AMQP broker {hostname}:{port}...")
    
    # Create credentials and connection parameters
    credentials = pika.PlainCredentials(username, password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=hostname,
            port=port,
            credentials=credentials,
            heartbeat=300,
            blocked_connection_timeout=300,
        )
    )
    print("Connected")

    print("Open channel")
    channel = connection.channel()

    # Set up the exchange if it doesn't exist
    print(f"Declare exchange: {exchange_name}")
    channel.exchange_declare(
        exchange=exchange_name, exchange_type=exchange_type, durable=True
    )
    # 'durable' makes the exchange survive broker restarts

    return channel

# Creates the individual queues attached to the exchange
def create_queue(channel, exchange_name, queue_name, routing_key):
    print(f"Bind to queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)
    # 'durable' makes the queue survive broker restarts

    # Bind the queue to the exchange via the routing key
    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=routing_key
    )

# Main execution
try:
    # Create the exchange
    channel = create_exchange(
        hostname=amqp_host,
        port=amqp_port,
        username=amqp_user,
        password=amqp_password,
        exchange_name=exchange_name,
        exchange_type=exchange_type,
    )

    # Create external_grading queue
    create_queue(
        channel=channel,
        exchange_name=exchange_name,
        queue_name="external_grading",
        routing_key="*.externalGrading",
    )

    # Create grading queue
    create_queue(
        channel=channel,
        exchange_name=exchange_name,
        queue_name="grading",
        routing_key="*.grading",
    )

    # Add .update binding key to grading queue
    create_queue(
        channel=channel,
        exchange_name=exchange_name,
        queue_name="grading",
        routing_key="*.update",
    )
    
    # Create delivery queue
    create_queue(
        channel=channel,
        exchange_name=exchange_name,
        queue_name="delivery",
        routing_key="*.delivery",
    )
    
    # Create notification queue
    create_queue(
        channel=channel,
        exchange_name=exchange_name,
        queue_name="notification",
        routing_key="*.notify",
    )

    # Create auction queue
    create_queue(
        channel=channel,
        exchange_name=exchange_name,
        queue_name="auction",
        routing_key="*.auction",
    )

finally:
    # Close the connection
    if 'channel' in locals() and channel.is_open:
        channel.close()
        print("Connection closed")