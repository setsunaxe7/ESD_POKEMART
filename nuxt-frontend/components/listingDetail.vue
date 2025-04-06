<script setup lang="ts">
    import type { Listing } from "~/types/listing";

    const props = defineProps<{
        listing: Listing;
    }>();

    // Format price with currency
    const formattedPrice = computed(() => {
        if (!props.listing.price) return "$0.00";
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(
            props.listing.type === "auction"
                ? props.listing.highest_bid || props.listing.price
                : props.listing.price
        );
    });

    // Calculate time remaining for auctions
    const timeRemaining = computed(() => {
        if (!props.listing?.auction_end_date) return null;
        const endDate = new Date(props.listing?.auction_end_date);
        const now = new Date();
        const diff = endDate.getTime() - now.getTime();

        if (diff <= 0) return "Auction ended";

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

        return `${days}d ${hours}h ${minutes}m`;
    });

    // Format date to readable format
    function formatDate(dateString: string) {
        return new Date(dateString).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
        });
    }

    // Determine badge color based on status
    const statusColor = computed(() => {
        switch (props.listing.status) {
            case "active":
                return "green";
            case "sold":
                return "blue";
            case "cancelled":
                return "red";
            default:
                return "gray";
        }
    });

    // Determine button properties
    const buttonProps = computed(() => {
        return props.listing.type === "direct"
            ? { color: "primary", label: "Buy Now" }
            : { color: "warning", label: "Bid Now" };
    });
</script>

<template>
    <NuxtLink :to="`/listing/${listing.id}`" class="block h-full">
        <UCard
            :ui="{ body: '!p-0' }"
            class="h-full transition-all duration-200 hover:shadow-md">
            <!-- Card Header with Image -->
            <div class="relative">
                <img
                    :src="
                        listing.image_url ||
                        'https://placehold.co/800x600/f3f4f6/d1d5db?text=No+Image'
                    "
                    :alt="listing.title"
                    class="w-full h-64 md:h-72 object-cover rounded-t-lg" />

                <!-- Listing Type Badge (Top Left) -->
                <UBadge class="absolute top-3 left-3 rounded-full" size="md">
                    {{ listing.type === "direct" ? "Buy Now" : "Auction" }}
                </UBadge>

                <!-- Time Remaining Badge (Top Right) - Only for Auctions -->
                <UBadge
                    v-if="listing.type === 'auction' && timeRemaining"
                    class="absolute top-3 right-3 flex items-center rounded-full"
                    color="error"
                    size="md">
                    <UIcon name="i-lucide-clock" class="mr-1 h-3 w-3" />
                    {{ timeRemaining }}
                </UBadge>
            </div>

            <!-- Card Body Content -->
            <div class="p-6 flex flex-col h-full">
                <!-- Title (Top) -->
                <div class="mb-2">
                    <h2 class="text-lg font-bold">{{ listing.title }}</h2>
                </div>

                <!-- Details Grid (Middle) -->
                <!-- <div class="grid grid-cols-2 gap-4 mb-auto">
                    <div>
                        <p class="text-xs text-gray-500">Card Grade</p>
                        <p class="font-medium text-sm">
                            {{ listing.grade === 0 ? "Ungraded" : `PSA ${listing.grade}` }}
                        </p>
                    </div>
                    <div>
                        <p class="text-xs text-gray-500">Listed On</p>
                        <p class="font-medium text-sm">{{ formatDate(listing.created_at) }}</p>
                    </div>
                </div> -->

                <!-- Bottom Row (Price left, Button right) -->
                <div class="flex items-center justify-between">
                    <!-- Price (Bottom Left) -->
                    <div>
                        <p class="text-xs text-gray-500">
                            {{ listing.type === "direct" ? "Price" : "Current Bid" }}
                        </p>
                        <p class="text-lg font-bold">
                            {{ formattedPrice }}
                        </p>
                    </div>

                    <!-- Action Button (Bottom Right) -->
                    <!-- <div class="flex items-end">
                        <UButton
                            size="md"
                            :to="`/listing/${listing.id}`">
                            {{ buttonProps.label }}
                        </UButton>
                    </div> -->
                </div>
            </div>
        </UCard>
    </NuxtLink>
</template>
