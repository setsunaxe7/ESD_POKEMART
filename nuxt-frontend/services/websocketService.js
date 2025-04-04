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

    subscribeToQueue(queue, onMessageReceived) {
        this.client.subscribe(`/queue/${queue}`, (message) => {
            if (message.body) {
                onMessageReceived(JSON.parse(message.body));
            }
        });
    }   

    subscribeToExchange(exchange, bindingKey, onMessageReceived) {
        this.client.subscribe(`/exchange/${exchange}/${bindingKey}`, (message) => {
            if (message.body) {
                onMessageReceived(JSON.parse(message.body));
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

    subscribeToBids(onMessageReceived) {
        this.subscribeToExchange("bidding_exchange", "", onMessageReceived);
    }

    disconnect() {
        if (this.client) {
            this.client.deactivate();
        }
    }
}

export default new WebSocketService();
