FROM rabbitmq:3-management

# Enable RabbitMQ Web STOMP plugin
RUN rabbitmq-plugins enable rabbitmq_web_stomp

# Expose required ports
EXPOSE 5672 15672 15674

# Start RabbitMQ
CMD ["rabbitmq-server"]


# for confs if it works
# FROM rabbitmq:3-management

# ADD rabbitmq.config /etc/rabbitmq/
# ADD definitions.json /etc/rabbitmq/
# RUN chown rabbitmq:rabbitmq /etc/rabbitmq/rabbitmq.config /etc/rabbitmq/definitions.json
# CMD ["rabbitmq-server"]