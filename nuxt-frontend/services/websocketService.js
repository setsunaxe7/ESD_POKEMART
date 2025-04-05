import { Client } from "@stomp/stompjs";

class WebSocketService {
    constructor() {
        this.client = null;
    }

    connect(url) {
        this.client = new Client({
            brokerURL: url, // Example: "ws://localhost:15674/ws"
            connectHeaders: {
                login: "guest",
                passcode: "guest"
            },
            debug: (str) => console.log(str),
            onConnect: () => {
                console.log("Connected to RabbitMQ WebSocket!");
                // this.subscribeToQueue(queue, onMessageReceived);
            },
            onStompError: (frame) => {
                console.error("Broker error: ", frame.headers["message"]);
            },
            reconnectDelay: 5000, // Auto-reconnect
        });

        this.client.activate();
    }

    connect(url, queue, onMessageReceived) {
        this.client = new Client({
            brokerURL: url, // Example: "ws://localhost:15674/ws"
            connectHeaders: {
                login: "guest",
                passcode: "guest"
            },
            debug: (str) => console.log(str),
            onConnect: () => {
                console.log("Connected to RabbitMQ WebSocket!");
                this.subscribeToQueue(queue, onMessageReceived);
            },
            onStompError: (frame) => {
                console.error("Broker error: ", frame.headers["message"]);
            },
            reconnectDelay: 5000, // Auto-reconnect
        });

        this.client.activate();
    }

    econnect(url, exchange, bindingKey, onMessageReceived) {
        this.client = new Client({
            brokerURL: url, // Example: "ws://localhost:15674/ws"
            connectHeaders: {
                login: "guest",
                passcode: "guest"
            },
            debug: (str) => console.log(str),
            onConnect: () => {
                console.log("Connected to RabbitMQ WebSocket!");
                this.subscribeToExchange(exchange, bindingKey, onMessageReceived);
            },
            onStompError: (frame) => {
                console.error("Broker error: ", frame.headers["message"]);
            },
            reconnectDelay: 5000, // Auto-reconnect
        });

        this.client.activate();
    }

    subscribeToQueue(queue, onMessageReceived) {
        if (!this.client) {
            console.error("WebSocket client is not connected!");
            return;
        }

        this.client.subscribe(`/queue/${queue}`, (message) => {
            if (message.body) {
                const parsedMessage = JSON.parse(message.body);
                console.log(`Received message from queue '${queue}':`, parsedMessage);
                onMessageReceived(parsedMessage);
            }
        });
    }

    // subscribeToExchange(exchange, bindingKey, onMessageReceived) {
    //     this.client.subscribe(`/exchange/${exchange}/${bindingKey}`, (message) => {
    //         if (message.body) {
    //             onMessageReceived(JSON.parse(message.body));
    //         }
    //     });
    // }

    subscribeToExchange(exchange, bindingKey, onMessageReceived) {
        if (!this.client) {
            console.error("WebSocket client is not connected!");
            return;
        }
    
        // Subscribe to the exchange with the specified binding key
        this.client.subscribe(`/exchange/${exchange}/${bindingKey}`, (message) => {
            if (message.body) {
                const parsedMessage = JSON.parse(message.body);
                console.log(`Received message from exchange '${exchange}' with binding key '${bindingKey}':`, parsedMessage);
                onMessageReceived(parsedMessage);
            }
        });
    }

    sendMessage(exchange, routingKey, message) {
        if (this.client && this.client.connected) {
            this.client.publish({
                destination: `/exchange/${exchange}/${routingKey}`, // Use exchange and routing key
                body: JSON.stringify(message),
            });
        }
    }

    // sendMessage(queue, message) {
    //     if (this.client && this.client.connected) {
    //         this.client.publish({
    //             destination: `/queue/${queue}`,
    //             body: JSON.stringify(message),
    //         });
    //     }
    // }

    // subscribeToBids(onMessageReceived) {
    //     this.subscribeToExchange("bidding_exchange", "", onMessageReceived);
    // }

    disconnect() {
        if (this.client) {
            this.client.deactivate();
        }
    }
}

export default new WebSocketService();
