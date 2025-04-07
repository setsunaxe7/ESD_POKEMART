<script setup lang="ts">
import { ref, onMounted } from "vue";
import { loadStripe } from "@stripe/stripe-js";

const stripe = ref(null); // Ref to hold the Stripe instance
const elements = ref(null); // Ref to hold the Elements instance
const cardElement = ref(null); // Ref to hold the CardElement instance
const cardMounted = ref(false);
const paymentResult = ref<string | null>(null);
const isProcessing = ref(false);

onMounted(async () => {
    try {
        // Initialize Stripe with your publishable key
        const stripeInstance = await loadStripe("pk_test_51RAWjj2KPPVAucgy3qsCuMX4BuqxpKYMxZa1KJ8JPqO29G5lHNMa4msRL1LuxXEcBbN5IovTIUcDODFSXCQjaVKl002kbrRYse");
        if (!stripeInstance) {
            throw new Error("Failed to initialize Stripe.");
        }

        stripe.value = stripeInstance; // Assign resolved Stripe instance
        elements.value = stripe.value.elements(); // Initialize Elements

        // Create and mount the CardElement
        cardElement.value = elements.value.create("card");
        cardElement.value.mount("#card-element");
        cardMounted.value = true;
    } catch (error) {
        console.error("Error initializing Stripe:", error);
    }
});

const handlePayment = async () => {
    isProcessing.value = true;
    paymentResult.value = null;

    try {
        // Step 1: Call Flask API to create a PaymentIntent
        const { clientSecret } = await $fetch<{ clientSecret: string }>(
            "http://localhost:8000/payment/create_payment_intent",
            {
                method: "POST",
                body: { amount: 1000, currency: "usd" }, // Example: $10.00 in USD
            }
        );

        // Step 2: Confirm the payment using Stripe.js
        const result = await stripe.value.confirmCardPayment(clientSecret, {
            payment_method: {
                card: cardElement.value,
                billing_details: {
                    name: "Customer Name", // Replace with dynamic customer name if needed
                },
            },
        });

        if (result.error) {
            paymentResult.value = `Payment failed: ${result.error.message}`;
        } else {
            paymentResult.value = "Payment successful!";
        }
    } catch (error) {
        console.error("Error processing payment:", error);
        paymentResult.value = `Error processing payment: ${error.message}`;
    } finally {
        isProcessing.value = false;
    }
};
</script>

<template>
    <UContainer>
        <UPageHero
            title="Make a Payment"
            description="Securely pay for your purchase using our trusted payment gateway powered by Stripe."
            orientation="horizontal">
            <img
                src="../assets/img/payment/payment.png"
                alt="Payment Illustration"
                class="rounded-lg shadow-2xl ring ring-(--ui-border)" />
        </UPageHero>

        <UPageSection title="Enter Your Payment Details" description="">
            <!-- Payment Form -->
            <form id="payment-form" @submit.prevent="handlePayment">
                <div id="card-element" class="border rounded-lg p-4 mb-4"></div>
                <button :disabled="isProcessing" class="btn btn-primary w-full">
                    {{ isProcessing ? "Processing..." : "Pay $10.00" }}
                </button>
            </form>

            <!-- Payment Result -->
            <div v-if="paymentResult" class="mt-4 p-4 bg-gray-100 rounded-lg">
                {{ paymentResult }}
            </div>
        </UPageSection>
    </UContainer>
</template>
