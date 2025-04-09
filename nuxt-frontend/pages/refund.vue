<script setup lang="ts">
    import { USelectMenu } from "#components";
    import axios from "axios";
    import type { Listing } from "~/types/listing";
    import { useCards } from "#imports";

    const payments = ref([]);
    const listings = ref<Listing[]>([]);
    const selectedTransaction = ref(null);
    const selectedReason = ref(null);
    const refundReason = ["Card Damaged", "Item not as described", "Others"];
    const elaboration = ref("");
    const transactionOptions = ref([]);
    const imageFile = ref(null);
    const isLoading = ref(true);
    const { card, fetchCard, cardLoading } = useCards();
    const isSubmitting = ref(false);
    const user = useSupabaseUser();
    const handleFileChange = (event: any) => {
        imageFile.value = event.target.files[0];
    };

    // Get user payments data
    const getUserPayments = async () => {
        const userId = user.value.id;
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

    // Form validation computed property
    const isFormValid = computed(() => {
        return (
            selectedTransaction.value && selectedReason.value && elaboration.value.trim().length > 0
        );
    });

    // Format date helper function (already exists in ListingDetail but needed here too)
    function formatDate(dateString) {
        if (!dateString) return "N/A";
        return new Date(dateString).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
        });
    }

    const selectedOrder = computed(() => {
        if (!selectedTransaction.value) return null;
        // Find the listing that matches the selected transaction ID
        const listing = listings.value.find(
            (listing) => listing.id === selectedTransaction.value?.value
        );

        return {
            listingData: listing || null,
        };
    });

    watch(
        selectedOrder,
        async (newValue) => {
            if (newValue?.listingData?.card_id) {
                try {
                    console.log("Fetching card data for:", newValue.listingData.card_id);
                    await fetchCard(newValue.listingData.card_id);
                    console.log("Card data fetched successfully:", card.value);
                } catch (error) {
                    console.error("Error fetching card data:", error);
                }
            } else {
                console.log("No card ID available in selected order");
            }
        },
        { immediate: true }
    );

    const submitRequest = async () => {
        isSubmitting.value = true;
    };

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
                const listingsData: Listing[] = await getListings(listingIds);
                listings.value = listingsData || [];
                console.log("Listings fetched:", listings.value.length);

                transactionOptions.value = listings.value.map((listing) => ({
                    label: `${listing.title} - $${listing.price}`,
                    value: listing.id,
                }));

                // Format options for the select menu
            }
        } catch (err) {
            console.error("Failed to initialize page:", err);
        } finally {
            isLoading.value = false;
            console.log(selectedOrder);
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
            <Loading v-if="isLoading"></Loading>
            <div v-else>
                <UCard class="p-4 mb-8">
                    <div class="space-y-8">
                        <div class="space-y-2">
                            <h1 class="text-2xl font-bold">Request form</h1>
                            <p class="text-gray-500">
                                Fill up this form accordingly to submit a refund request for review
                            </p>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-16">
                            <!-- Left Column - Form Fields -->
                            <div class="col-span-1 flex flex-col space-y-6">
                                <div class="space-y-2">
                                    <p class="font-medium">Choose Order</p>
                                    <USelectMenu
                                        v-model="selectedTransaction"
                                        class="w-full"
                                        :items="transactionOptions"
                                        placeholder="Select transaction" />
                                </div>
                                <div class="space-y-2">
                                    <p class="font-medium">Reason For Request</p>
                                    <USelectMenu
                                        v-model="selectedReason"
                                        class="w-full"
                                        :items="refundReason"
                                        placeholder="Select reason" />
                                </div>
                                <div class="space-y-2">
                                    <p class="font-medium">Elaboration For Reason</p>
                                    <UTextarea
                                        v-model="elaboration"
                                        class="w-full"
                                        placeholder="Provide a detailed explanation for the reason of this refund request"
                                        :rows="4" />
                                </div>
                                <div>
                                    <p class="font-medium">Upload Evidence</p>
                                    <UInput
                                        class="mt-2 w-full"
                                        type="file"
                                        @change="handleFileChange" />
                                </div>
                                <div class="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg border border-gray-100 mt-4">
                                    <div class="flex items-start space-x-3">
                                        <div>
                                            <div class="flex flex-row space-x-2">
                                                <h4 class="font-bold text-sm mb-1">
                                                    Important Information
                                                </h4>
                                                <UIcon
                                                    name="i-lucide-info"
                                                    class="text-red-400 flex-shrink-0 mt-0.5" />
                                            </div>
                                            <p class="text-sm text-gray-500">
                                                All refund requests are subject to review. Please
                                                ensure you provide accurate information and
                                                supporting evidence for your claim. Processing may
                                                take up to 5-7 business days once approved.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Right Column - Order Preview Card -->
                            <div class="col-span-1">
                                <!-- Placeholder when no order is selected -->
                                <UCard
                                    v-if="!selectedTransaction"
                                    class="h-full flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-gray-800 text-center">
                                    <UIcon
                                        name="i-lucide-package"
                                        class="text-gray-300 w-16 h-16 mb-4 mx-auto" />
                                    <h3 class="text-lg font-medium text-gray-500">Order Preview</h3>
                                    <p class="text-sm text-gray-400 mt-2">
                                        Select an order to view its details
                                    </p>
                                </UCard>

                                <UCard v-else class="h-full">
                                    <div v-if="cardLoading" class="mt-8">
                                        <Loading class="mx-auto"></Loading>
                                    </div>
                                    <div v-else>
                                        <p class="font-bold text-lg mb-4">
                                            Order - {{ selectedOrder?.listingData?.title }}
                                        </p>
                                        <div class="flex flex-col">
                                            <div>
                                                <img
                                                    class="m-auto"
                                                    :src="selectedOrder?.listingData?.image_url" />
                                            </div>
                                            <USeparator class="my-4"></USeparator>
                                            <div>
                                                <p class="font-bold mb-2">Details</p>
                                                <div class="flex flex-row space-x-12">
                                                    <div>
                                                        <p class="text-gray-400 text-sm">
                                                            Card Name
                                                        </p>
                                                        <p class="font-medium text-sm">
                                                            {{ card?.name }}
                                                        </p>
                                                    </div>
                                                    <div>
                                                        <p class="text-gray-400 text-sm">
                                                            Seller Name
                                                        </p>
                                                        <p class="font-medium text-sm">
                                                            {{
                                                                selectedOrder?.listingData
                                                                    ?.seller_name
                                                            }}
                                                        </p>
                                                    </div>
                                                    <div>
                                                        <p class="text-gray-400 text-sm">
                                                            Listed On
                                                        </p>
                                                        <p class="font-medium text-sm">
                                                            {{
                                                                formatDate(
                                                                    selectedOrder?.listingData
                                                                        ?.created_at
                                                                )
                                                            }}
                                                        </p>
                                                    </div>
                                                    <div>
                                                        <p class="text-gray-400 text-sm">
                                                            Order Price
                                                        </p>
                                                        <p class="font-medium text-sm">
                                                            ${{ selectedOrder?.listingData?.price }}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </UCard>
                            </div>
                        </div>
                    </div>
                </UCard>
                <div class="w-full flex my-4">
                    <UButton
                        size="xl"
                        :block="true"
                        class="w-1/4 m-auto"
                        :disabled="!isFormValid"
                        @click="submitRequest()">
                        Submit Request
                    </UButton>
                </div>
            </div>
        </UContainer>
    </UMain>
</template>
