<script setup lang="ts">
    import { ref, onMounted, computed, onUnmounted } from 'vue';
    
    // websocket module
    import WebSocketService from "../services/websocketService.js";

    // Mounted
    onMounted(async () => {
        // connect to RabbitMQ
        WebSocketService.connect("ws://localhost:15674/ws");
    });

    onUnmounted(() => {
        WebSocketService.disconnect();
    });

    //  -------------------------------------------------------------

    // RabbitMQ functions
    const exchange = "grading_topic";

    // Receive Message function
    const userRequests = ref("");

    // Send message function
    const sendMessage = (routingKey ,jsonStr) => {
        WebSocketService.sendMessage(exchange, routingKey, jsonStr);
    };

    //  -------------------------------------------------------------
    
    const gradingID = ref("");

    //  -------------------------------------------------------------

    // Submit form/ integration w backend
    function externalSubmitForm() {
        const jsonStr = {
            gradingID: gradingID.value,
        }
        sendMessage("update.externalGrading", jsonStr);
        gradingID.value = "";
        return;
    }

    //  -------------------------------------------------------------
</script>

<template>
<UMain>
    <UContainer class="truncate-page">
        <UFormField label="Grading ID">
            <UInput 
                v-model="gradingID" 
                placeholder="Enter grading ID" 
                class="w-full"
            />
        </UFormField>
        <UButton @click="externalSubmitForm">Truncate grading</UButton>
    </UContainer>
</UMain>
</template>