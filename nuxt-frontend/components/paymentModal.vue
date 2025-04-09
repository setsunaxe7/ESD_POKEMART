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

interface ListingStatus {
    status: string;
}
    const router = useRouter();

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
                    const stripeInstance = await loadStripe(
                        "pk_test_51RAWjj2KPPVAucgy3qsCuMX4BuqxpKYMxZa1KJ8JPqO29G5lHNMa4msRL1LuxXEcBbN5IovTIUcDODFSXCQjaVKl002kbrRYse"
                    );
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

        // Verify listing status from marketplace API
        const marketplaceResponse = await $fetch<ListingStatus>(
            `http://localhost:8000/marketplace/api/marketplace/listings/${listingId}`
        );

        const listingStatus = marketplaceResponse.status;

        if (listingStatus !== "active") {
            // Show error message if listing is not active
            paymentResult.value = `Payment failed: Listing is ${listingStatus}. Payment cannot be processed.`;
            console.error(`Listing ${listingId} is ${listingStatus}. Payment cannot proceed.`);
            paymentStatus.value = "failed";
            return;
        }

        // Update listing status to "pending"
        await $fetch(`http://localhost:8000/marketplace/api/marketplace/listings/${listingId}`, {
            method: "PUT",
            body: {
                status: "pending", // Update the status to 'pending'
            },
        });

        console.log(`Listing ${listingId} status updated to pending.`);



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

                // await $fetch(`http://localhost:8000/marketplace/api/marketplace/listings/${listingId}`, {
                //     method: "PUT",
                //     headers: {
                //         "Content-Type": "application/json",
                //     },
                //     body: {
                //         status: "closed", // Update the status to 'closed'
                //     },
                // });

                await $fetch(
                    `http://localhost:8000/marketplace/api/marketplace/listings/${listingId}`,
                    {
                        method: "PUT",
                        body: {
                            status: "closed",
                        },
                    }
                );

                paymentResult.value = "Payment successful!";
                paymentStatus.value = "success";
                emit("payment-success");
            }
        } catch (error) {
            console.error("Error processing payment:", error);
            paymentResult.value = `Error processing payment: ${error.message}`;
            paymentStatus.value = "failed";
        } finally {
            isProcessing.value = false;
        }
    };

    const paymentStatus = ref<"idle" | "success" | "failed">("idle");

    // Helper function to format amount
    const formatAmount = (amt: number) => {
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: currency.toUpperCase(),
        }).format(amt / 100);
    };

    const resetForm = () => {
        paymentStatus.value = "idle";
        paymentResult.value = null;

        // Re-initialize elements if needed
        nextTick(() => {
            // Your Stripe elements re-mounting code if needed
        });
    };

    const closeModal = () => {
        // Reset state before closing
        if (paymentStatus.value !== "idle") {
            paymentStatus.value = "idle";
        }
        emit("close");
        // Navigate to marketplace
        router.push("/marketplace");
    };
</script>

<template>
    <div v-if="show" class="modal-overlay">
        <div class="modal-content w-[500px] px-12 py-8">
            <!-- Payment Success View -->
            <div v-if="paymentStatus === 'success'" class="text-center py-6">
                <UIcon name="i-lucide-check-circle" class="w-16 h-16 text-green-500 mx-auto mb-4" />
                <h2 class="text-2xl font-bold text-green-700 mb-2">Payment Successful!</h2>
                <p class="text-gray-600 mb-6">
                    Your payment of {{ formatAmount(amount) }} {{ currency }} has been processed
                    successfully.
                </p>
                <USeparator class="my-4" />
                <p class="text-sm text-gray-500 mb-4">
                    Order details have been sent to your email.
                </p>
                <UButton @click="closeModal" color="primary" size="lg">Continue Shopping</UButton>
            </div>

            <!-- Payment Failed View -->
            <div v-else-if="paymentStatus === 'failed'" class="text-center py-6">
                <UIcon name="i-lucide-x-circle" class="w-16 h-16 text-red-500 mx-auto mb-4" />
                <h2 class="text-2xl font-bold text-red-700 mb-2">Payment Failed</h2>
                <p class="text-gray-600 mb-6">There was an error processing your payment.</p>
                <div class="bg-red-50 p-4 rounded-lg mb-6 text-left">
                    <p class="text-sm text-red-800">{{ paymentResult }}</p>
                </div>
                <!-- <div class="flex flex-col space-y-2"> -->
                <div class="space-x-4">
                    <UButton @click="resetForm" color="primary" size="lg">Try Again</UButton>
                    <UButton @click="closeModal" color="neutral" variant="outline" size="lg">
                        Cancel
                    </UButton>
                </div>

                <!-- </div> -->
            </div>

            <!-- Payment Form -->
            <div v-else>
                <h2 class="text-xl font-semibold">Enter Payment Details</h2>
                <USeparator class="my-4" />
                <form class="space-y-2" id="payment-form" @submit.prevent="handlePayment">
                    <!-- Card Number Field -->
                    <label
                        for="card-number-element"
                        class="block text-sm font-medium text-gray-700">
                        Card Number
                    </label>
                    <div id="card-number-element" class="stripe-input mb-4"></div>

                    <!-- Expiry Date Field -->
                    <label
                        for="card-expiry-element"
                        class="block text-sm font-medium text-gray-700">
                        Expiration Date
                    </label>
                    <div id="card-expiry-element" class="stripe-input mb-4"></div>

                    <!-- CVC Field -->
                    <label for="card-cvc-element" class="block text-sm font-medium text-gray-700">
                        CVC
                    </label>
                    <div id="card-cvc-element" class="stripe-input mb-4"></div>

                    <!-- Payment Total -->
                    <div class="flex justify-between items-center py-2">
                        <span class="text-sm font-medium text-gray-700">Total payment:</span>
                        <span class="font-bold text-lg">
                            {{ formatAmount(amount) }} {{ currency }}
                        </span>
                    </div>

                    <!-- Submit Button -->
                    <div class="flex flex-row justify-center">
                        <UButton
                            type="submit"
                            :loading="isProcessing"
                            :disabled="isProcessing"
                            color="primary"
                            class="mt-4"
                            size="lg">
                            {{ isProcessing ? "Processing..." : "Complete Payment" }}
                        </UButton>
                    </div>
                </form>
                <button
                    @click="closeModal"
                    class="w-full text-center text-gray-500 mt-4 py-2 hover:underline cursor-pointer text-sm">
                    Cancel
                </button>
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
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        max-height: 90vh;
        overflow-y: auto;
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

    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }

    .modal-overlay {
        animation: fadeIn 0.2s ease-out;
    }
</style>
