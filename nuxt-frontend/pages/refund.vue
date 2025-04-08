<script setup lang="ts">
    import { USelectMenu } from "#components";
    import axios from "axios";

    const payments = ref([]);
    const listings = ref([]);
    const selectedTransaction = ref(null);
    const selectedReason = ref(null);
    const refundReason = ["Card Damaged", "Item not as described", "Others"];
    const elaboration = ref("");
    const transactionOptions = ref([]);

    // Get user payments data
    const getUserPayments = async () => {
        const userId = "d4abad07-1209-4170-b4d5-bd1d088cfde1";

        try {
            const response = await axios.get(`http://localhost:8000/payment/payments/${userId}`);

            // Check if the request was successful
            if (response.status === 200) {
                console.log("Payment information retrieved successfully:", response.data);
                return response.data.payments;
            }
        } catch (error) {
            // Handle errors
            if (error.response) {
                // The request was made and the server responded with a status code outside of 2xx
                console.error("Error fetching payment data:", error.response.data);
                console.error("Status:", error.response.status);
            } else if (error.request) {
                // The request was made but no response was received
                console.error("No response received:", error.request);
            } else {
                // Something happened in setting up the request that triggered an Error
                console.error("Error setting up request:", error.message);
            }
            throw error;
        }
    };

    // Get listings based on listing IDs
    const getListings = async (listingIds) => {
        try {
            const response = await axios.post(
                "http://localhost:8000/marketplace/api/marketplace/listings/batch",
                { listing_ids: listingIds }
            );

            if (response.status === 200) {
                console.log("Listings retrieved successfully:", response.data);
                return response.data;
            }
        } catch (error) {
            console.error("Error fetching listings:", error.response?.data || error.message);
            throw error;
        }
    };

    // Format payment data for select menu
    const formatPaymentOptions = (paymentsData, listingsData) => {
        // Create a map of listing ID to listing details for quick lookups
        const listingMap = {};
        listingsData.forEach((listing) => {
            listingMap[listing.id] = listing;
        });

        return paymentsData
            .filter((payment) => payment.status === "succeeded") // Only show successful payments
            .map((payment) => {
                const listing = listingMap[payment.listing_id];
                const amount = (payment.amount / 100).toFixed(2); // Convert cents to dollars

                return {
                    label: `${listing?.title || "Unknown item"} - $${amount}`,
                    value: payment.payment_intent_id,
                    paymentData: payment,
                    listingData: listing,
                };
            });
    };

    // Submit refund request
    // const submitRefundRequest = async () => {
    //     if (!selectedTransaction.value || !selectedReason.value) {
    //         alert("Please select a transaction and reason for refund");
    //         return;
    //     }

    //     const payment = payments.value.find(
    //         (p) => p.payment_intent_id === selectedTransaction.value
    //     );

    //     if (!payment) return;

    //     try {
    //         const response = await axios.post("http://localhost:8000/payment/refund", {
    //             payment_intent_id: payment.payment_intent_id,
    //             reason: selectedReason.value,
    //             amount: payment.amount, // Full refund
    //         });

    //         if (response.status === 200) {
    //             alert("Refund request submitted successfully");
    //             // Reset form
    //             selectedTransaction.value = null;
    //             selectedReason.value = null;
    //             elaboration.value = "";
    //         }
    //     } catch (error) {
    //         console.error("Error submitting refund:", error);
    //         alert("Failed to submit refund request");
    //     }
    // };

    onMounted(async () => {
        try {
            // Get payment data
            const paymentsData = await getUserPayments();
            payments.value = paymentsData || [];
            console.log("Total payments:", payments.value.length);

            if (payments.value.length > 0) {
                // Extract unique listing IDs from payments
                const listingIds = [
                    ...new Set(
                        payments.value
                            .filter((p) => p.listing_id) // Filter out payments without listing_id
                            .map((p) => p.listing_id)
                    ),
                ];
                console.log("Listing IDs to fetch:", listingIds);

                // Fetch listing details for these IDs
                const listingsData = await getListings(listingIds);
                listings.value = listingsData || [];
                console.log("Listings fetched:", listings.value.length);

                // Format options for the select menu
                transactionOptions.value = formatPaymentOptions(payments.value, listings.value);
            }
        } catch (err) {
            console.error("Failed to initialize page:", err);
        }
    });
</script>

<template>
    <UMain class="min-h-[calc(100vh-var(--header-height)-var(--footer-height))]">
        <UContainer>
            <UPageSection
                title="Refund Request"
                description="Submit a refund request for an unsatisfactory order"
                :ui="{ container: 'lg:py-24' }" />
            <UCard class="p-4 mb-8">
                <div class="space-y-8">
                    <div class="space-y-2">
                        <h1 class="text-2xl font-bold">Request form</h1>
                        <p class="text-gray-500">
                            Fill up this form accordingly to submit a refund request for review
                        </p>
                    </div>
                    <div class="grid grid-cols-3 gap-12">
                        <div class="col-span-2 flex flex-col space-y-6">
                            <div class="space-y-2">
                                <p class="font-medium">Choose an order</p>
                                <USelectMenu
                                    v-model="selectedTransaction"
                                    class="w-3/4"
                                    :items="transactionOptions"
                                    placeholder="Select transaction"></USelectMenu>
                            </div>
                            <div class="space-y-2">
                                <p class="font-medium">Reason for request</p>
                                <USelectMenu
                                    v-model="selectedReason"
                                    class="w-3/4"
                                    :items="refundReason"
                                    placeholder="Select reason"></USelectMenu>
                            </div>
                            <div class="space-y-2">
                                <p class="font-medium">Elaboration for reason</p>
                                <UTextarea
                                    v-model="elaboration"
                                    class="w-3/4"
                                    placeholder="Provide a detailed explanation for the reason of this refund request"
                                    :rows="4"></UTextarea>
                            </div>
                        </div>
                    </div>
                </div>
            </UCard>
            <div class="w-full flex">
                <UButton size="xl" :block="true" class="w-1/2 m-auto">Submit Request</UButton>
            </div>
        </UContainer>
    </UMain>
</template>
