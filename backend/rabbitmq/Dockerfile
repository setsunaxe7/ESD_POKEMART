FROM rabbitmq:3-management

# Enable RabbitMQ Web STOMP plugin
RUN rabbitmq-plugins enable rabbitmq_web_stomp

# Expose required ports
EXPOSE 5672 15672 15674

# Start RabbitMQ
CMD ["rabbitmq-server"]
