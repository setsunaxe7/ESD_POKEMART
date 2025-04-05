import pika

def on_message_callback(ch, method, properties, body):
    print(f"Received message: {body}")

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue="auction", durable=True)
channel.basic_consume(queue="auction", on_message_callback=on_message_callback, auto_ack=True)

print("Waiting for messages...")
channel.start_consuming()
