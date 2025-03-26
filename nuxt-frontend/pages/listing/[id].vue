<script setup lang="ts">
    import { ref, onMounted, computed } from "vue";
    import type { Listing } from "~/types/listing";
    import type { BreadcrumbItem } from "@nuxt/ui";
    import type { Card } from "~/types/card";

    // Get the route to access the ID parameter
    const route = useRoute();
    const id = route.params.id as string;

    // State variables
    const listing = ref<Listing>();
    const isLoading = ref(true);
    const error = ref<string | null>(null);
    const bidAmount = ref<number | null>(null);
    const listingCard = ref<Card>();

    let breadCrumb = ref<BreadcrumbItem[]>([
        {
            label: "Home",
            icon: "i-lucide-house",
        },
        {
            label: "Marketplace",
            icon: "i-lucide-box",
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
                `http://localhost:5004/api/marketplace/listings/${id}`
            );
            listing.value = response;
            const cardResponse = await $fetch<Card>(
                `http://localhost:5003/inventory/${listing.value.card_id}`
            );
            listingCard.value = cardResponse;
            breadCrumb.value = [
                {
                    label: "Home",
                    icon: "i-lucide-house",
                },
                {
                    label: "Marketplace",
                    icon: "i-lucide-box",
                    to: "/marketplace",
                },
                {
                    label: listing.value.title,
                    icon: "i-iconoir:pokeball",
                    to: "/listing/" + id,
                },
            ];
        } catch (err: any) {
            error.value = err.message || "Failed to load listing";
            console.error(error.value);
        } finally {
            isLoading.value = false;
        }
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
</script>

<template>
    <UMain>
        <UContainer class="mt-12 space-y-8">
            <!-- Loading state -->
            <UBreadcrumb :items="breadCrumb" />
            <Loading v-if="isLoading"></Loading>
            <div v-else class="grid grid-cols-7 gap-8">
                <div class="col-span-3 justify-content-center">
                    <img :src="listing?.image_url" class="object-fit-contain" />
                </div>
                <div class="col-span-4">
                    <UCard class="p-4">
                        <h1 class="font-semibold text-3xl mb-2">{{ listing?.title }}</h1>
                        <div v-if="listing?.description" class="flex flex-col">
                            <p class="text-gray-500">Description</p>
                            <p class="font-medium">{{ listing.description }}</p>
                        </div>
                        <USeparator class="my-4"></USeparator>
                        <div class="grid grid-cols-2 grid-rows-2">
                            <div class="flex flex-col">
                                <p class="text-gray-500">Card Name</p>
                                <p class="font-medium">{{ listingCard?.name }}</p>
                            </div>
                        </div>
                    </UCard>
                </div>
            </div>
        </UContainer>
    </UMain>
</template>
