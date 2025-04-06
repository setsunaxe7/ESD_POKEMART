<script setup lang="ts">
    import { ref, onMounted, computed } from "vue";
    import type { Listing } from "~/types/listing";
    import type { BreadcrumbItem } from "@nuxt/ui";
    import type { Card } from "~/types/card";
    import WebSocketService from "../../services/websocketService.js";

    interface BidUpdateMessage {
        listing_id: string;
        highest_bid: number;
    }



    // Get the route to access the ID parameter
    const route = useRoute();
    const id = route.params.id as string;

    // State variables
    const listing = ref<Listing>();
    const isLoading = ref(true);
    const error = ref<string | null>(null);
    const bidAmount = ref<number | null>(null);
    const listingCard = ref<Card>();
    const highestBid = ref<number | null>(null);

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
            isLoading.value = true;
            const response = await $fetch<Listing>(
                `http://localhost:8000/marketplace/api/marketplace/listings/${id}`
            );
            listing.value = response;
            const cardResponse = await $fetch<Card>(
                `http://localhost:8000/inventory/inventory/${listing.value.card_id}`
            );
            listingCard.value = cardResponse;
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

            highestBid.value = listing.value.highest_bid || 0;

            // Connect to WebSocket and subscribe to bid updates
            WebSocketService.econnect("ws://localhost:15674/ws", "grading_topic", "*.auction", (message) => {
                if (message.listing_id === id) {
                    highestBid.value = message.highest_bid;
                    console.log(`Highest bid updated to ${message.highest_bid}`);
                }
            });


        } catch (err: any) {
            error.value = err.message || "Failed to load listing";
            console.error(error.value);
        } finally {
            isLoading.value = false;
        }
    });

    // onMounted(() => {
    //     WebSocketService.connect("ws://localhost:15674/ws");
    //     // WebSocketService.subscribeToQueue("grading", onMessageReceived);
    // });

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
        if (!highestBid.value) return "$0.00";
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(highestBid.value);
    });


    // Implement placeBid
    async function placeBid() {
        console.log("Attempting to place bid: $" + bidAmount.value);
        try {
            if (!bidAmount.value || bidAmount.value <= 0) {
                console.error("Invalid bid amount");
                return;
            }

            const response = await $fetch('http://localhost:8000/bid/bid', {
                method: 'POST',
                body: {
                    auctionId: id, // ID of the listing
                    bidAmount: bidAmount.value, // User's bid amount
                    buyerId: '123e4567-e89b-12d3-a456-426614174001', // Replace with actual user ID (if available)
                },
            });

            console.log("Bid placed successfully:", response);
            const updatedBidCount = (listing.value?.bid_count || 0) + 1;

            const response2 = await $fetch(`http://localhost:8000/marketplace/api/marketplace/listings/${id}`, {
                method: 'PUT',
                body: {
                    id: id, // ID of the listing
                    highest_bid: bidAmount.value, // User's bid amount
                    highest_bidder_id: '123e4567-e89b-12d3-a456-426614174001', // Replace with actual user ID (if available)
                    bid_count: updatedBidCount,
                },
            });

            console.log("Listing data updated successfully:", response2);

        } catch (error) {
            console.error("Error placing bid:", error);
        }

    }

    // Implement placeOrder
    function placeOrder() {
        console.log("Place order");
    }
</script>

<template>
    <UMain>
        <UContainer class="mt-12 space-y-8">
            <!-- Loading state -->
            <UBreadcrumb :items="breadCrumb" />
            <Loading class="mt-24" v-if="isLoading"></Loading>
            <div v-else class="grid grid-cols-7 gap-8">
                <div
                    class="col-span-3 bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
                    <img
                        :src="listing?.image_url"
                        :alt="listing?.title"
                        class="max-h-full max-w-full object-contain p-4" />
                </div>
                <div class="col-span-4 space-y-6">
                    <UCard>
                        <h1 class="font-semibold text-3xl mb-2">{{ listing?.title }}</h1>
                        <div v-if="listing?.description" class="flex flex-col">
                            <p class="text-gray-500 text-sm">Description</p>
                            <p class="font-medium">{{ listing.description }}</p>
                        </div>
                        <USeparator class="my-4"></USeparator>
                        <div class="grid grid-cols-2 grid-rows-2 gap-4">
                            <div class="flex flex-col col-span-1 row-span-1">
                                <p class="text-gray-500 text-sm">Card Name</p>
                                <p class="font-medium">{{ listingCard?.name }}</p>
                            </div>
                            <div class="flex flex-col col-span-1 row-span-1">
                                <p class="text-gray-500 text-sm">Card Rarity</p>
                                <p class="font-medium">{{ listingCard?.rarity }}</p>
                            </div>
                            <div class="flex flex-col col-span-1 row-span-1">
                                <p class="text-gray-500 text-sm">Card Grade</p>
                                <p class="font-medium">{{ listing?.grade }}</p>
                            </div>
                            <div class="flex flex-col col-span-1 row-span-1">
                                <p class="text-gray-500 text-sm">Listing Type</p>
                                <p class="font-medium capitalize">{{ listing?.type }}</p>
                            </div>
                        </div>
                    </UCard>
                    <UCard v-if="isAuction">
                        <div class="grid grid-cols-2 grid-rows-2">
                            <div class="flex flex-col col-span-1 row-span-1">
                                <p class="text-gray-500 text-sm">Current Bid</p>
                                <p class="font-medium capitalize">{{ listing?.type == "auction" ? formattedHighestBid : formattedPrice }}</p>
                            </div>
                            <div class="flex flex-col col-span-1 row-span-1">
                                <p class="text-gray-500 text-sm">Auction Ends In</p>
                                <p class="font-medium capitalize">{{ timeRemaining }}</p>
                            </div>
                            <div class="flex flex-col col-span-1 row-span-1">
                                <p class="text-gray-500 text-sm mb-2">Place Bid</p>
                                <div class="w-full">
                                    <UInput
                                        class="w-3/4"
                                        type="number"
                                        v-model="bidAmount"></UInput>
                                </div>
                            </div>
                            <div class="flex flex-col col-span-1 row-span-1 self-end">
                                <UButton size="lg" @click="placeBid()" :block="true">
                                    Place bid
                                </UButton>
                            </div>
                        </div>
                    </UCard>
                    <UCard v-else>
                        <div class="grid grid-cols-2 grid-rows-1">
                            <div class="flex flex-col col-span-1">
                                <p class="text-gray-500 text-sm">Listing Price</p>
                                <p class="font-medium capitalize">{{ formattedPrice }}</p>
                            </div>
                            <div class="flex flex-col col-span-1 self-end">
                                <UButton size="lg" @click="placeOrder()" :block="true">
                                    Place Order
                                </UButton>
                            </div>
                        </div>
                    </UCard>
                </div>
            </div>
        </UContainer>
    </UMain>
</template>
