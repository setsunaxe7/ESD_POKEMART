<script setup lang="ts">
    import { ref, onMounted, computed } from "vue";
    import type { Listing } from "~/types/listing";
    import type { BreadcrumbItem } from "@nuxt/ui";
    import type { Card } from "~/types/card";
    import WebSocketService from "../../services/websocketService.js";
    import PaymentModal from "~/components/paymentModal.vue";

    interface BidUpdateMessage {
        listing_id: string;
        highest_bid: number;
    }

    const supabase = useSupabaseClient();

    const showPaymentModal = ref(false); // Controls visibility of the modal
    const paymentAmount = ref<number | null>(null); // Holds the price for the payment modal

    // Get the route to access the ID parameter
    const route = useRoute();
    const id = route.params.id as string;

    // State variables
    const listing = ref<Listing>();
    const bidInfo = ref();
    const isLoading = ref(true);
    const error = ref<string | null>(null);
    const bidAmount = ref<number | null>(null);
    const listingCard = ref<Card>();
    const highestBid = ref<number | null>(null);

    // User data variables
    const userId = ref<string | null>(null); // Store user ID
    const displayName = ref<string | null>(null); // Store display name

    let breadCrumb = ref<BreadcrumbItem[]>([
        {
            label: "Home",
            icon: "i-lucide-house",
        },
        {
            label: "Marketplace",
            icon: "i-lucide-store",
            to: "/marketplace",
        },
        {
            label: "Loading...",
            icon: "i-lucide-link",
        },
    ]);

    // Fetch the specific listing by ID
    onMounted(async () => {
        try {
            fetchUserData();
            isLoading.value = true;
            const response = await $fetch<Listing>(
                `http://localhost:8000/marketplace/api/marketplace/listings/${id}`
            );
            listing.value = response;
            const cardResponse = await $fetch<Card>(
                `http://localhost:8000/inventory/inventory/${listing.value.card_id}`
            );
            const bidResponse = await $fetch<any>(
                `http://localhost:8000/bid/bids/${listing.value.id}`
            );
            listingCard.value = cardResponse;
            bidInfo.value = bidResponse;
            console.log(bidInfo);
            breadCrumb.value = [
                {
                    label: "Home",
                    icon: "i-lucide-house",
                },
                {
                    label: "Marketplace",
                    icon: "i-lucide-store",
                    to: "/marketplace",
                },
                {
                    label: listing.value.title,
                    icon: "i-iconoir:pokeball",
                    to: "/listing/" + id,
                },
            ];

            highestBid.value = listing.value.highest_bid || listing.value.price;

            // Connect to WebSocket and subscribe to bid updates
            WebSocketService.econnect(
                "ws://localhost:15674/ws",
                "grading_topic",
                "*.auction",
                (message) => {
                    if (message.listing_id === id) {
                        highestBid.value = message.highest_bid;
                        console.log(`Highest bid updated to ${message.highest_bid}`);
                    }
                }
            );
        } catch (err: any) {
            error.value = err.message || "Failed to load listing";
            console.error(error.value);
        } finally {
            isLoading.value = false;
        }
    });

    onUnmounted(() => {
        WebSocketService.disconnect();
    });

    // Computed properties
    const isAuction = computed(() => listing.value?.type === "auction");
    const timeRemaining = computed(() => {
        if (!listing.value?.auction_end_date) return null;
        const endDate = new Date(listing.value.auction_end_date);
        const now = new Date();
        const diff = endDate.getTime() - now.getTime();

        if (diff <= 0) return "Auction ended";

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

        return `${days}d ${hours}h ${minutes}m`;
    });

    const formattedPrice = computed(() => {
        if (!listing.value?.price) return "$0.00";
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(listing.value.price);
    });

    const formattedHighestBid = computed(() => {
        // Use highest bid if available, otherwise fall back to listing price
        const bidAmount = highestBid.value || listing.value?.price || 0;

        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(bidAmount);
    });

    async function fetchUserData() {
        try {
            const { data, error } = await supabase.auth.getUser(); // Get user data from Supabase
            if (error) {
                console.error("Error fetching user data:", error);
                return;
            }
            if (data && data.user) {
                console.log("User ID:", data.user.id); // Unique identifier for the user
                console.log("Display Name:", data.user.user_metadata?.display_name || "N/A"); // Display name

                // Store user data into reactive variables
                userId.value = data.user.id;
                displayName.value = data.user.user_metadata?.display_name || "N/A";
            } else {
                console.log("No logged-in user found.");
            }
        } catch (error) {
            console.error("Error fetching user data:", error);
        }
    }

    // Implement placeBid
    async function placeBid() {
        console.log("Attempting to place bid: $" + bidAmount.value);
        try {
            if (!bidAmount.value || bidAmount.value <= 0) {
                console.error("Invalid bid amount");
                return;
            }

            const response = await $fetch("http://localhost:8000/bid/bid", {
                method: "POST",
                body: {
                    auctionId: id, // ID of the listing
                    bidAmount: bidAmount.value, // User's bid amount
                    buyerId: userId.value, // Replace with actual user ID (if available)
                    timestamp: new Date().toISOString(), // Add the current timestamp
                },
            });

            console.log("Bid placed successfully:", response);
            const updatedBidCount = (listing.value?.bid_count || 0) + 1;

            const response2 = await $fetch(
                `http://localhost:8000/marketplace/api/marketplace/listings/${id}`,
                {
                    method: "PUT",
                    body: {
                        id: id, // ID of the listing
                        highest_bid: bidAmount.value, // User's bid amount
                        highest_bidder_id: userId.value, // Replace with actual user ID (if available)
                        bid_count: updatedBidCount,
                    },
                }
            );

            console.log("Listing data updated successfully:", response2);
        } catch (error) {
            console.error("Error placing bid:", error);
        }
    }

    // Implement placeOrder
    function placeOrder() {
        console.log("Place order");
        showPaymentModal.value = true; // Show the payment modal
        paymentAmount.value = listing.value?.price || 0; // Pass the price to the modal
    }
</script>

<template>
    <UMain>
        <UContainer class="mt-12 space-y-8">
            <!-- Loading state -->
            <UBreadcrumb :items="breadCrumb" />
            <Loading class="mt-24" v-if="isLoading"></Loading>
            <div v-else>
                <div class="grid grid-cols-7 gap-16">
                    <!-- Left column - Image -->
                    <div class="col-span-4">
                        <div
                            class="bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center overflow-hidden h-full">
                            <img
                                :src="listing?.image_url"
                                :alt="listing?.title"
                                class="max-h-full max-w-full object-contain p-4" />
                        </div>
                    </div>

                    <!-- Right column - Listing details with bid/buy below -->
                    <div class="col-span-3 space-y-6">
                        <!-- Listing details -->
                        <div class="space-y-4 p-4">
                            <h1 class="font-bold text-4xl">{{ listing?.title }}</h1>
                            <div v-if="listing?.description" class="flex flex-col">
                                <p class="text-gray-500 text-sm">Description</p>
                                <p class="font-medium text-md">{{ listing.description }}</p>
                            </div>
                            <USeparator class="my-4"></USeparator>
                            <h1 class="font-bold text-xl">Listing Details</h1>
                            <div class="grid grid-cols-2 grid-rows-2 gap-4 gap-x-12">
                                <div class="flex flex-col col-span-1 row-span-1">
                                    <p class="text-gray-500 text-sm">Card Name</p>
                                    <p class="font-medium text-md">{{ listingCard?.name }}</p>
                                </div>
                                <div class="flex flex-col col-span-1 row-span-1">
                                    <p class="text-gray-500 text-sm">Card Rarity</p>
                                    <p class="font-medium text-md">{{ listingCard?.rarity }}</p>
                                </div>
                                <div class="flex flex-col col-span-1 row-span-1">
                                    <p class="text-gray-500 text-sm">Card Grade</p>
                                    <p class="font-medium text-md">{{ listing?.grade }}</p>
                                </div>
                                <div class="flex flex-col col-span-1 row-span-1">
                                    <p class="text-gray-500 text-sm">Seller Name</p>
                                    <p class="font-medium capitalize text-md">
                                        {{ listing?.seller_name }}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <!-- Purchase/Bid Card - Same width as details -->
                        <div class="pt-4">
                            <!-- Bid form - Only for auctions -->
                            <UCard v-if="isAuction">
                                <div class="grid grid-cols-2 gap-4 gap-x-12 mb-6">
                                    <div class="flex flex-col">
                                        <p class="text-gray-500 text-sm">Starting Price</p>
                                        <p class="font-medium text-md">{{ formattedPrice }}</p>
                                    </div>
                                    <div class="flex flex-col">
                                        <p class="text-gray-500 text-sm">Auction Ends In</p>
                                        <p class="font-medium text-md">{{ timeRemaining }}</p>
                                    </div>
                                    <div class="flex flex-col">
                                        <p class="text-gray-500 text-sm">Current Bid</p>
                                        <p class="font-bold text-xl">
                                            {{ formattedHighestBid }}
                                        </p>
                                    </div>
                                    <div class="flex flex-col">
                                        <p class="text-gray-500 text-sm">Total Bids</p>
                                        <p class="font-medium text-md">
                                            {{ listing?.bid_count || 0 }}
                                        </p>
                                    </div>
                                </div>

                                <div class="flex flex-col md:flex-row items-end gap-8">
                                    <div class="w-1/2">
                                        <p class="text-gray-500 text-sm mb-2">Bid Amount</p>
                                        <UInput
                                            type="number"
                                            placeholder="Enter bid amount"
                                            v-model="bidAmount"
                                            class="w-full" />
                                    </div>
                                    <UButton
                                        size="lg"
                                        @click="placeBid()"
                                        class="w-full md:w-auto">
                                        Place Bid
                                    </UButton>
                                </div>
                            </UCard>

                            <!-- Buy now button - Only for direct listings -->
                            <UCard v-else>
                                <div
                                    class="flex flex-col md:flex-row items-center justify-between gap-4">
                                    <div>
                                        <p class="text-gray-500 text-sm">Listing Price</p>
                                        <p class="font-bold text-xl">{{ formattedPrice }}</p>
                                    </div>
                                    <UButton
                                        size="lg"
                                        @click="placeOrder()"
                                        color="primary"
                                        class="w-full md:w-auto">
                                        Buy Now
                                    </UButton>
                                </div>
                            </UCard>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Payment Modal -->
            <PaymentModal
                :show="showPaymentModal"
                :amount="paymentAmount * 100"
                currency="USD"
                :user-id="userId || ''"
                :listing-id="id"
                @close="showPaymentModal = false" />
        </UContainer>
    </UMain>
</template>
