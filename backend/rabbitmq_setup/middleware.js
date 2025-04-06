// consumer.js
const amqp = require('amqplib');
const axios = require('axios');

// 🔧 Correct RabbitMQ container service name
// const RABBITMQ_URL = 'amqp://admin:admin@localhost:5673';  Change to service name
const EXCHANGE_NAME = 'bulba.topic';
const QUEUE_NAME = 'notification.queue';
const ROUTING_KEY = '*.inform';

// 🔗 Replace this with your actual OutSystems API endpoint
const OUTSYSTEMS_API = 'https://personal-gvra7qzz.outsystemscloud.com/Notification/rest/NotificationAPI/api/notification/receive';

async function connectWithRetry(attempt = 1) {
  try {
    console.log(`🔁 Trying AMQP connection (attempt ${attempt})...`);
    const conn = await amqp.connect(RABBITMQ_URL);
    const channel = await conn.createChannel();

    // Assert exchange and queue
    await channel.assertExchange(EXCHANGE_NAME, 'topic', { durable: true });
    await channel.assertQueue(QUEUE_NAME, { durable: true });

    // Bind to only *.inform
    await channel.bindQueue(QUEUE_NAME, EXCHANGE_NAME, ROUTING_KEY);

    console.log(`✅ Connected. Listening to ${QUEUE_NAME} with routing key "${ROUTING_KEY}"`);

    // Start consuming
    channel.consume(QUEUE_NAME, async (msg) => {
      if (msg !== null) {
        const data = JSON.parse(msg.content.toString());
        console.log("📨 Incoming Message:", data);

        try {
          const response = await axios.post(OUTSYSTEMS_API, data, {
            headers: { 'Content-Type': 'application/json' },
          });
          console.log("✅ Forwarded to OutSystems:", response.status);
          channel.ack(msg);
        } catch (err) {
          console.error("❌ Failed to forward:", err.response?.data || err.message);
          channel.nack(msg, false, false); // Drop the message (or set to true to requeue)
        }
      }
    });
  } catch (err) {
    console.error(`❌ AMQP connection failed (attempt ${attempt}):`, err.message);
    setTimeout(() => connectWithRetry(attempt + 1), 5000);
  }
}

connectWithRetry();

