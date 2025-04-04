<script setup>
import { ref, onMounted, onUnmounted } from "vue";




// const messages = ref([]);
// const queue = "myQueue"; // Replace with your RabbitMQ queue name

// const onMessageReceived = (msg) => {
//     console.log("Received:", msg);
//     messages.value.push(msg);
// };

// onMounted(() => {
//     WebSocketService.connect("ws://localhost:15674/ws", queue, onMessageReceived);
// });

// onUnmounted(() => {
//     WebSocketService.disconnect();
// });

// const sendMessage = () => {
//     WebSocketService.sendMessage(queue, { text: "Hello from Vue!" });
// };
</script>

<template>
    <div>
        <h2>AMQP WebSocket Messages</h2>
        <UButton @click="sendMessage">Send Message</UButton>
        <ul>
            <li v-for="(msg, index) in messages" :key="index">
                {{ msg.text }}
            </li>
        </ul>
    </div>
</template>
