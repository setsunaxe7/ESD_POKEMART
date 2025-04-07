<script setup lang="ts">
    import { ref, onMounted } from "vue";
    import type { Listing } from "../types/listing";
    import type { RadioGroupItem, RadioGroupValue } from "@nuxt/ui";
    import WebSocketService from "../services/websocketService.js";

    const listings = ref<Listing[]>([]);
    const allListings = ref<Listing[]>([]);
    const currentPage = ref(1);
    const itemsPerPage = ref(6);
    let totalRange = [0, 0];
    const isLoading = ref(true);
    const radioItems = ref<RadioGroupItem[]>(["All", "Direct", "Auction"]);

    const paginatedListings = computed(() => {
        const startIndex = (currentPage.value - 1) * itemsPerPage.value;
        const endIndex = startIndex + itemsPerPage.value;
        return listings.value.slice(startIndex, endIndex);
    });

    // Fetch Cards from API
    onMounted(async () => {
        try {
            const response = await $fetch<Listing[]>(
                "http://localhost:8000/marketplace/api/marketplace/listings"
            );
            listings.value = response; // Assign API response to listings
            allListings.value = response;
            // Set initial price range based on data
            if (response.length > 0) {
                const prices = response.map((l) =>
                    l.type === "auction" && l.highest_bid ? l.highest_bid : l.price
                );
                filters.value.priceRange = [
                    Math.floor(Math.min(...prices)),
                    Math.ceil(Math.max(...prices)),
                ];
                totalRange = [Math.floor(Math.min(...prices)), Math.ceil(Math.max(...prices))];
            }

            // Connect to WebSocket server
            WebSocketService.connect("ws://localhost:15674/ws");
            WebSocketService.subscribeToBids((message) => {
                const { listing_id, highest_bid } = message;

                // Find the relevant listing and update its highest_bid dynamically
                const listingToUpdate = listings.value.find(
                    (listing) => listing.id === listing_id && listing.type === "auction"
                );
                if (listingToUpdate) {
                    listingToUpdate.highest_bid = highest_bid;
                }
                const route = useRoute();
                if (route.query.page) {
                    const pageNum = parseInt(route.query.page as string);
                    if (!isNaN(pageNum) && pageNum > 0) {
                        currentPage.value = pageNum;
                    }
                }
            });
            sortListings(value.value);
        } catch (error) {
            console.error("Error fetching marketplace listings:", error);
        } finally {
            isLoading.value = false;
        }
    });

    // Filter states
    const filters = ref({
        searchQuery: "",
        type: [] as ("direct" | "auction")[],
        gradeRange: [0, 10],
        priceRange: totalRange,
    });

    // Computed filtered listings
    const filteredListings = computed(() => {
        return allListings.value.filter((listing) => {
            // Search query filter
            if (
                filters.value.searchQuery &&
                !listing.title.toLowerCase().includes(filters.value.searchQuery.toLowerCase())
            ) {
                return false;
            }

            // Type filter
            if (filters.value.type.length > 0 && !filters.value.type.includes(listing.type)) {
                return false;
            }

            // Grade filter
            if (
                listing.grade < filters.value.gradeRange[0] ||
                listing.grade > filters.value.gradeRange[1]
            ) {
                return false;
            }

            // Price filter (use highest_bid for auctions if available)
            const listingPrice =
                listing.type === "auction" && listing.highest_bid
                    ? listing.highest_bid
                    : listing.price;

            if (
                listingPrice < filters.value.priceRange[0] ||
                listingPrice > filters.value.priceRange[1]
            ) {
                return false;
            }

            return true;
        });
    });

    // Reset all filters
    const resetFilters = () => {
        filters.value = {
            searchQuery: "",
            type: [],
            gradeRange: [0, 10],
            priceRange: totalRange,
        };
    };

    const selectedTypeValue = computed({
        get() {
            // Return appropriate radio value based on filters.type
            if (filters.value.type.length === 0) {
                return "All";
            } else if (filters.value.type.includes("direct")) {
                return "Direct";
            } else if (filters.value.type.includes("auction")) {
                return "Auction";
            }
            return "All"; // Default value
        },
        set(newValue) {
            // Update filters.type when radio selection changes
            if (newValue === "All") {
                filters.value.type = [];
            } else if (newValue === "Direct") {
                filters.value.type = ["direct"];
            } else if (newValue === "Auction") {
                filters.value.type = ["auction"];
            }
        },
    });

    // Apply filters when they change
    watch(
        filters,
        () => {
            currentPage.value = 1;
            listings.value = filteredListings.value;
            sortListings(value.value);
        },
        { deep: true }
    );

    const items = ref([
        "Recent",
        "Grade",
        "Sort: A to Z",
        "Sort: Z to A",
        "$: Low to High",
        "$: High to Low",
    ]);
    const value = ref("Recent");

    const sortListings = (sortOption: string) => {
        const sortedListings = [...listings.value];

        switch (sortOption) {
            case "Recent":
                // Sort by created_at date (newest first)
                sortedListings.sort((a, b) => {
                    const dateA = new Date(a.created_at).getTime();
                    const dateB = new Date(b.created_at).getTime();
                    return dateB - dateA; // Descending order (newest first)
                });
                break;
            case "Sort: A to Z":
                sortedListings.sort((a, b) => a.title.localeCompare(b.title));
                break;
            case "Sort: Z to A":
                sortedListings.sort((a, b) => b.title.localeCompare(a.title));
                break;
            case "$: Low to High":
                sortedListings.sort((a, b) => {
                    const aPrice = a.type === "auction" && a.highest_bid ? a.highest_bid : a.price;
                    const bPrice = b.type === "auction" && b.highest_bid ? b.highest_bid : b.price;
                    return aPrice - bPrice;
                });
                break;
            case "$: High to Low":
                sortedListings.sort((a, b) => {
                    const aPrice = a.type === "auction" && a.highest_bid ? a.highest_bid : a.price;
                    const bPrice = b.type === "auction" && b.highest_bid ? b.highest_bid : b.price;
                    return bPrice - aPrice;
                });
                break;
            case "Grade":
                sortedListings.sort((a, b) => b.grade - a.grade);
                break;
        }

        listings.value = sortedListings;
    };

    watch(value, (newSortOption) => {
        if (newSortOption) {
            sortListings(newSortOption);
        }
    });

    const hasActiveFilters = computed(() => {
        return (
            filters.value.searchQuery.trim() !== "" ||
            filters.value.type.length > 0 ||
            filters.value.gradeRange[0] !== 0 ||
            filters.value.gradeRange[1] !== 10 ||
            filters.value.priceRange[0] !== totalRange[0] ||
            filters.value.priceRange[1] !== totalRange[1]
        );
    });

    function to(page: number) {
        return {
            query: {
                page,
            },
        };
    }
</script>


<template>
    <UMain class="mb-12">
        <UContainer>
            <UPageSection
                title="Marketplace"
                description="Find and purchase the Pokémon cards you're looking for"
                :ui="{ container: 'lg:py-24' }" />
            <Loading v-if="isLoading"></Loading>
            <div v-else class="flex flex-col lg:flex-row gap-8">
                <!-- Sticky Side Menu for Filters -->
                <div class="lg:w-1/4 lg:sticky block top-24 space-y-8 h-fit">
                    <UCard>
                        <h3 class="text-lg font-bold mb-4">Search</h3>
                        <UInput
                            class="w-full"
                            v-model="filters.searchQuery"
                            placeholder="Search listings..."
                            icon="i-lucide-search" />
                    </UCard>
                    <UCard>
                        <div class="flex flex-row justify-between align-middle mb-4">
                            <h3 class="text-lg font-bold">Filters</h3>
                            <!-- Reset Filters Button -->
                            <UButton
                                color="neutral"
                                leading-icon="i-lucide-x"
                                v-if="hasActiveFilters"
                                variant="ghost"
                                @click="resetFilters">
                                Clear Filters
                            </UButton>
                        </div>

                        <!-- Price Range Filter -->
                        <div>
                            <h4 class="font-medium mb-4">Price Range</h4>
                            <USlider
                                v-model="filters.priceRange"
                                :step="10"
                                :min="totalRange[0]"
                                :max="totalRange[1]" />
                            <div class="flex justify-between text-sm text-gray-500 mt-2">
                                <span>${{ filters.priceRange[0] }}</span>
                                <span>${{ filters.priceRange[1] }}</span>
                            </div>
                        </div>

                        <USeparator class="my-4"></USeparator>

                        <!-- Grade Range Filter -->
                        <div>
                            <h4 class="font-medium mb-4">Card Grade</h4>
                            <USlider v-model="filters.gradeRange" :min="0" :max="10" :step="1" />
                            <div class="flex justify-between text-sm text-gray-500 mt-2">
                                <span>
                                    {{
                                        filters.gradeRange[0] === 0
                                            ? "Ungraded"
                                            : `PSA ${filters.gradeRange[0]}`
                                    }}
                                </span>
                                <span>PSA {{ filters.gradeRange[1] }}</span>
                            </div>
                        </div>

                        <USeparator class="my-4"></USeparator>
                        <!-- Type Filter -->
                        <div>
                            <h4 class="font-medium mb-4">Listing Type</h4>
                            <URadioGroup v-model="selectedTypeValue" :items="radioItems" />
                        </div>
                    </UCard>
                </div>

                <!-- Main Content Grid -->
                <div class="lg:w-3/4">
                    <div class="flex flex-row w-full justify-between">
                        <p class="text-center font-medium">{{ filteredListings.length }} Listings</p>
                        <div class="flex items-center gap-2">
                            <USelect class="w-36" v-model="value" :items="items" />
                        </div>
                    </div>
                    <USeparator class="my-4"></USeparator>
                    <!-- Listings Grid -->
                    <div class="h-full" v-if="filteredListings.length === 0">
                        <UCard
                            class="h-full flex flex-col items-center justify-center text-center p-8">
                            <UIcon
                                name="i-heroicons-magnifying-glass-20-solid"
                                class="mx-auto mb-4 w-12 h-12 text-gray-400" />
                            <p class="text-lg font-medium text-gray-500 dark:text-white">
                                No listings found
                            </p>
                            <p class="mt-2 text-gray-500 dark:text-white">
                                Try adjusting your filters to find what you're looking for.
                            </p>
                            <UButton class="mt-6" @click="resetFilters">Clear Filters</UButton>
                        </UCard>
                    </div>

                    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <ListingDetail
                            v-for="listing in paginatedListings"
                            :key="listing.id"
                            :listing="listing"
                            class="h-full" />
                    </div>
                    <div class="flex flex-row justify-center" v-if="filteredListings.length !== 0">
                        <UPagination
                            class="mt-12"
                            :to="to"
                            v-model:page="currentPage"
                            :items-per-page="itemsPerPage"
                            :total="listings.length" />
                    </div>
                </div>
            </div>
        </UContainer>
    </UMain>
</template>
