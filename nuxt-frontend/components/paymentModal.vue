<script setup lang="ts">
import { ref, watch, nextTick } from "vue";
import { loadStripe } from "@stripe/stripe-js";

const stripe = ref(null); // Ref to hold the Stripe instance
const elements = ref(null); // Ref to hold the Elements instance
const cardNumber = ref(null); // Ref to hold the CardNumberElement instance
const cardExpiry = ref(null); // Ref to hold the CardExpiryElement instance
const cardCvc = ref(null); // Ref to hold the CardCvcElement instance
const cardMounted = ref(false);
const paymentResult = ref<string | null>(null);
const isProcessing = ref(false);

// Props passed from parent component
const { show, amount, currency, userId, listingId } = defineProps({
    show: {
        type: Boolean,
        required: true,
    },
    amount: {
        type: Number,
        required: true,
    },
    currency: {
        type: String,
        default: "usd",
    },
    userId: {
        type: String,
        required: true, 
    },
    listingId: {
        type: String,
        required: true, 
    },
});


// Emits events to parent component
const emit = defineEmits(["close", "payment-success", "payment-failed"]);

// Watch for modal visibility and initialize Stripe when visible
watch(
    () => show,
    async (isVisible) => {
        if (isVisible && !cardMounted.value) {
            try {
                const stripeInstance = await loadStripe("pk_test_51RAWjj2KPPVAucgy3qsCuMX4BuqxpKYMxZa1KJ8JPqO29G5lHNMa4msRL1LuxXEcBbN5IovTIUcDODFSXCQjaVKl002kbrRYse");
                if (!stripeInstance) {
                    throw new Error("Failed to initialize Stripe.");
                }

                stripe.value = stripeInstance;
                elements.value = stripe.value.elements();

                // Use nextTick to ensure DOM elements exist before mounting
                await nextTick();

                // Mount individual elements
                cardNumber.value = elements.value.create("cardNumber");
                cardNumber.value.mount("#card-number-element");

                cardExpiry.value = elements.value.create("cardExpiry");
                cardExpiry.value.mount("#card-expiry-element");

                cardCvc.value = elements.value.create("cardCvc");
                cardCvc.value.mount("#card-cvc-element");

                cardMounted.value = true;
            } catch (error) {
                console.error("Error initializing Stripe:", error);
            }
        }
    }
);

const handlePayment = async () => {
    isProcessing.value = true;
    paymentResult.value = null;

    try {
        // Ensure amount is an integer
        const validAmount = parseInt(amount); // Convert amount to an integer
        const validCurrency = String(currency); // Ensure currency is a string
        console.log("Valid Amount:", validAmount, "Currency:", validCurrency, "User ID:", userId, "Listing ID:", listingId); // Log validated props

        // Step 1: Call backend to create PaymentIntent
        const { clientSecret } = await $fetch<{ clientSecret: string }>(
            "http://localhost:8000/payment/create_payment_intent",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json", // Ensure JSON content type
                },
                body: { 
                    amount: validAmount,
                    currency: validCurrency,
                    userId,
                    listingId,
                },
            }
        );

        console.log("Client Secret:", clientSecret); // Log client secret received from backend

        // Step 2: Confirm payment using Stripe.js
        const result = await stripe.value.confirmCardPayment(clientSecret, {
            payment_method: {
                card: elements.value.getElement("cardNumber"), // Use CardNumberElement for payment method
                billing_details: {
                    name: "Customer Name", // Replace with dynamic customer name if needed
                },
            },
        });

        if (result.error) {
            paymentResult.value = `Payment failed: ${result.error.message}`;
            emit("payment-failed", result.error.message);
        } else {

            console.log("Payment successful:", result.paymentIntent.status);
            // Step 3: Update payment status in backend
            await $fetch("http://localhost:8000/payment/update_payment_status", {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: {
                        payment_intent_id: result.paymentIntent.id,
                        status: result.paymentIntent.status,
                    },
                });

            paymentResult.value = "Payment successful!";
            emit("payment-success");
        }
    } catch (error) {
        console.error("Error processing payment:", error);
        paymentResult.value = `Error processing payment: ${error.message}`;
    } finally {
        isProcessing.value = false;
    }
};





const closeModal = () => {
    emit("close"); // Notify parent to close the modal
};
</script>




<template>
    <div v-if="show" class="modal-overlay">
        <div class="modal-content">
            <h2 class="text-xl font-semibold mb-4">Enter Payment Details</h2>
            <form id="payment-form" @submit.prevent="handlePayment">
                <!-- Card Number Field -->
                <label for="card-number-element" class="block text-sm font-medium text-gray-700">Card Number</label>
                <div id="card-number-element" class="stripe-input mb-4"></div>

                <!-- Expiry Date Field -->
                <label for="card-expiry-element" class="block text-sm font-medium text-gray-700">Expiration Date</label>
                <div id="card-expiry-element" class="stripe-input mb-4"></div>

                <!-- CVC Field -->
                <label for="card-cvc-element" class="block text-sm font-medium text-gray-700">CVC</label>
                <div id="card-cvc-element" class="stripe-input mb-4"></div>

                <!-- Submit Button -->
                <button :disabled="isProcessing" class="btn btn-primary w-full">
                    {{ isProcessing ? "Processing..." : `Pay ${(amount / 100).toFixed(2)} ${currency}` }}
                </button>
            </form>
            <button @click="closeModal" class="btn btn-neutral w-full mt-4">Cancel</button>

            <!-- Payment Result -->
            <div v-if="paymentResult" class="mt-4 p-4 bg-gray-100 rounded-lg">
                {{ paymentResult }}
            </div>
        </div>
    </div>
</template>


<style scoped>
.modal-overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.5); /* Dimmed background */
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 50;
}

.modal-content {
    background-color: white;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}

.stripe-input {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 12px;
    min-height: 40px; /* Ensure minimum height for interactivity */
}
button.btn-primary {
    background-color: var(--ui-primary);
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
}

button.btn-neutral {
    background-color: var(--ui-neutral);
}
</style>


