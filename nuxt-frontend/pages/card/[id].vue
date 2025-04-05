<script setup lang="ts">
    import { useCards, useListings } from "#imports";
    import axios from "axios";
    import type { BreadcrumbItem, TabsItem } from "@nuxt/ui";
    import { USeparator } from "#components";
    const { card, cardLoading, cardError, fetchCard } = useCards();
    const { listings, isListingLoading, listingError, fetchListings } = useListings();

    // Get the route to access the ID parameter
    const route = useRoute();
    const id = route.params.id as string;

    type PokemonCard = {
        id: string;
        name: string;
        supertype: string;
        subtypes: string[];
        hp: string;
        types: string[];
        evolvesTo?: string[];
        attacks: Attack[];
        weaknesses?: Weakness[];
        retreatCost: string[];
        convertedRetreatCost: number;
        set: Set;
        number: string;
        artist: string;
        rarity: string;
        flavorText?: string;
        nationalPokedexNumbers: number[];
        legalities: Legalities;
        regulationMark: string;
        images: Images;
        tcgplayer: TCGPlayer;
        cardmarket: CardMarket;
    };

    type Attack = {
        name: string;
        cost: string[];
        convertedEnergyCost: number;
        damage: string;
        text?: string;
    };

    type Weakness = {
        type: string;
        value: string;
    };

    type Set = {
        id: string;
        name: string;
        series: string;
        printedTotal: number;
        total: number;
        legalities: Legalities;
        releaseDate: string;
        updatedAt: string;
        images: {
            symbol: string;
            logo: string;
        };
    };

    type Legalities = {
        unlimited: string;
        standard: string;
        expanded: string;
    };

    type Images = {
        small: string;
        large: string;
    };

    type TCGPlayer = {
        url: string;
        updatedAt: string;
        prices: {
            reverseHolofoil?: PriceData;
            normal?: PriceData;
        };
    };

    type PriceData = {
        low: number;
        mid: number;
        high: number;
        market: number;
        directLow: number | null;
    };

    type CardMarket = {
        url: string;
        updatedAt: string;
        prices: {
            averageSellPrice: number;
            lowPrice: number;
            trendPrice: number;
            germanProLow: number;
            suggestedPrice: number;
            reverseHoloSell: number;
            reverseHoloLow: number;
            reverseHoloTrend: number;
            lowPriceExPlus: number;
            avg1: number;
            avg7: number;
            avg30: number;
            reverseHoloAvg1: number;
            reverseHoloAvg7: number;
            reverseHoloAvg30: number;
        };
    };

    const directListings = computed(() => {
        if (!listings.value) return [];
        return listings.value.filter((listing) => listing.type === "direct");
    });

    const auctionListings = computed(() => {
        if (!listings.value) return [];
        return listings.value.filter((listing) => listing.type === "auction");
    });

    // Refs for Pokemon TCG data
    const tcgCard = ref<PokemonCard | null>(null);
    const isTcgLoading = ref(false);
    const tcgError = ref(null);

    const fetchPokemonTcgCard = async (cardId: string) => {
        try {
            isTcgLoading.value = true;
            tcgError.value = null;

            // Get API key from runtime config
            const apiKey: any = useRuntimeConfig().public.POKEMON_TCG_KEY;

            // Make request with authentication header
            const response = await axios.get(`https://api.pokemontcg.io/v2/cards/${cardId}`, {
                headers: {
                    "X-Api-Key": apiKey,
                },
            });

            tcgCard.value = response.data.data;
            console.log("TCG Card data:", tcgCard.value);
            return response.data.data;
        } catch (err: any) {
            tcgError.value = err.message || "Failed to fetch card from Pokemon TCG API";
            console.error("TCG API Error:", tcgError.value);
            return null;
        } finally {
            isTcgLoading.value = false;
        }
    };

    function getTimeRemaining(endDateStr: string | null) {
        if (!endDateStr) return "No end date";

        const endDate = new Date(endDateStr);
        const now = new Date();
        const diff = endDate.getTime() - now.getTime();

        if (diff <= 0) return "Auction ended";

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

        return `${days}d ${hours}h ${minutes}m`;
    }

    let breadCrumb = ref<BreadcrumbItem[]>([
        {
            label: "Home",
            icon: "i-lucide-house",
        },
        {
            label: "Collection",
            icon: "i-lucide-database",
            to: "/collection/page/1",
        },
        {
            label: "Loading...",
            icon: "i-lucide-loader-circle",
        },
    ]);

    const items = computed<TabsItem[]>(() => [
        {
            label: `All listings (${listings.value?.length || 0})`,
            slot: "all",
        },
        {
            label: `Buy Now (${directListings.value.length || 0})`,
            slot: "direct",
        },
        {
            label: `Auctions (${auctionListings.value.length || 0})`,
            slot: "auction",
        },
    ]);

    onMounted(async () => {
        // Fetch card from our database
        await fetchCard(id);

        await fetchListings({ card_id: String(card.value?.id) });

        if (card.value?.card_id) {
            await fetchPokemonTcgCard(card.value.card_id);
        }

        breadCrumb.value = [
            {
                label: "Home",
                icon: "i-lucide-house",
            },
            {
                label: "Collection",
                icon: "i-lucide-database",
                to: "/collection/page/1",
            },
            {
                label: card.value?.name,
                icon: "i-iconoir:pokeball",
                to: "/listing/" + id,
            },
        ];
    });
</script>

<template>
    <UMain>
        <UContainer class="my-12">
            <UBreadcrumb :items="breadCrumb" />
            <Loading class="mt-24" v-if="isTcgLoading && cardLoading"></Loading>
            <div v-if="!(isTcgLoading && cardLoading)" class="grid grid-cols-7 gap-24 mt-12">
                <div class="col-span-3">
                    <img class="w-full" :src="card?.high_res_image" />
                </div>
                <div class="col-span-4 space-y-4">
                    <div class="space-y-2">
                        <h1 class="font-bold text-4xl">{{ card?.name }}</h1>
                        <p class="text-gray-500">
                            {{ tcgCard?.set.series }} - {{ tcgCard?.set.name }}
                        </p>
                    </div>
                    <USeparator />
                    <div class="grid grid-cols-2 grid-rows-2 gap-4">
                        <div class="col-span-1 row-span-1">
                            <p class="text-gray-500 text-sm">Rarity</p>
                            <p class="font-medium text-md">{{ tcgCard?.rarity }}</p>
                        </div>
                        <div class="col-span-1 row-span-1">
                            <p class="text-gray-500 text-sm">Release Date</p>
                            <p class="font-medium text-md">{{ tcgCard?.set.releaseDate }}</p>
                        </div>
                        <div class="col-span-1 row-span-1">
                            <p class="text-gray-500 text-sm">Type</p>
                            <p class="font-medium text-md">{{ tcgCard?.types[0] }}</p>
                        </div>
                        <div class="col-span-1 row-span-1">
                            <p class="text-gray-500 text-sm">Artist</p>
                            <p class="font-medium text-md">{{ tcgCard?.artist }}</p>
                        </div>
                    </div>
                    <USeparator />
                    <div class="space-y-4">
                        <h1 class="font-bold text-xl">Market Listings</h1>
                        <UTabs :items="items">
                            <template #all="{ item }">
                                <div v-if="isListingLoading" class="py-4">
                                    <ULoading />
                                </div>
                                <UCard v-else-if="!listings?.length" class="mt-4 bg-gray-50">
                                    <div class="py-4 text-center text-gray-500">
                                        No listings found for this card
                                    </div>
                                </UCard>
                                <div v-else class="grid grid-cols-1 gap-4 py-4">
                                    <UCard
                                        v-for="listing in listings"
                                        :key="listing.id"
                                        class="hover:bg-gray-50 transition">
                                        <div class="flex justify-between items-start">
                                            <div>
                                                <h3 class="font-bold">{{ listing.title }}</h3>
                                                <p class="text-sm text-gray-500">
                                                    Grade:
                                                    {{
                                                        listing.grade === 0
                                                            ? "Ungraded"
                                                            : `PSA ${listing.grade}`
                                                    }}
                                                </p>
                                                <p
                                                    v-if="listing.type === 'auction'"
                                                    class="text-sm text-red-500 font-medium flex items-center">
                                                    <UIcon name="i-lucide-clock" class="mr-1" />
                                                    {{ getTimeRemaining(listing.auction_end_date) }}
                                                </p>
                                            </div>
                                            <div class="text-right">
                                                <div
                                                    v-if="listing.type === 'direct'"
                                                    class="font-bold text-primary">
                                                    ${{ listing.price.toFixed(2) }}
                                                </div>
                                                <div v-else>
                                                    <div class="font-bold">
                                                        ${{
                                                            (
                                                                listing.highest_bid || listing.price
                                                            ).toFixed(2)
                                                        }}
                                                    </div>
                                                    <p class="text-xs">Current Bid</p>
                                                </div>
                                                <UButton
                                                    class="mt-2"
                                                    :to="`/listing/${listing.id}`"
                                                    :color="
                                                        listing.type === 'direct'
                                                            ? 'primary'
                                                            : 'error'
                                                    "
                                                    size="md">
                                                    {{
                                                        listing.type === "direct"
                                                            ? "Buy Now"
                                                            : "View Auction"
                                                    }}
                                                </UButton>
                                            </div>
                                        </div>
                                    </UCard>
                                </div>
                            </template>
                            <template #direct="{ item }">
                                <div v-if="isListingLoading" class="py-4">
                                    <ULoading />
                                </div>
                                <UCard v-else-if="!directListings?.length" class="mt-4 bg-gray-50">
                                    <div class="py-4 text-center text-gray-500">
                                        No direct listings found for this card
                                    </div>
                                </UCard>
                                <div v-else class="grid grid-cols-1 gap-4 py-4 listing-scroll">
                                    <UCard
                                        v-for="listing in directListings"
                                        :key="listing.id"
                                        class="hover:bg-gray-50 transition">
                                        <div class="flex justify-between items-start">
                                            <div>
                                                <h3 class="font-bold">{{ listing.title }}</h3>
                                                <p class="text-sm text-gray-500">
                                                    Grade:
                                                    {{
                                                        listing.grade === 0
                                                            ? "Ungraded"
                                                            : `PSA ${listing.grade}`
                                                    }}
                                                </p>
                                            </div>
                                            <div class="text-right">
                                                <div class="font-bold text-primary">
                                                    ${{ listing.price.toFixed(2) }}
                                                </div>
                                                <UButton
                                                    class="mt-2"
                                                    :to="`/listing/${listing.id}`"
                                                    color="primary"
                                                    size="md">
                                                    Buy Now
                                                </UButton>
                                            </div>
                                        </div>
                                    </UCard>
                                </div>
                            </template>
                            <template #auction="{ item }">
                                <div v-if="isListingLoading" class="py-4">
                                    <ULoading />
                                </div>
                                <UCard v-else-if="!auctionListings?.length" class="mt-4 bg-gray-50">
                                    <div class="py-4 text-center text-gray-500">
                                        No auction listings found for this card
                                    </div>
                                </UCard>
                                <div v-else class="grid grid-cols-1 gap-4 py-4 listing-scroll">
                                    <UCard
                                        v-for="listing in auctionListings"
                                        :key="listing.id"
                                        class="hover:bg-gray-50 transition">
                                        <div class="flex justify-between items-start">
                                            <div>
                                                <h3 class="font-bold">{{ listing.title }}</h3>
                                                <p class="text-sm text-gray-500">
                                                    Grade:
                                                    {{
                                                        listing.grade === 0
                                                            ? "Ungraded"
                                                            : `PSA ${listing.grade}`
                                                    }}
                                                </p>
                                                <p
                                                    class="text-sm text-red-500 font-medium flex items-center">
                                                    <UIcon name="i-lucide-clock" class="mr-1" />
                                                    {{ getTimeRemaining(listing.auction_end_date) }}
                                                </p>
                                            </div>
                                            <div class="text-right">
                                                <div class="font-bold">
                                                    ${{
                                                        (
                                                            listing.highest_bid || listing.price
                                                        ).toFixed(2)
                                                    }}
                                                </div>
                                                <p class="text-xs">Current Bid</p>
                                                <UButton
                                                    class="mt-2"
                                                    :to="`/listing/${listing.id}`"
                                                    color="error"
                                                    size="md">
                                                    View Auction
                                                </UButton>
                                            </div>
                                        </div>
                                    </UCard>
                                </div>
                            </template>
                        </UTabs>
                    </div>
                </div>
            </div>
        </UContainer>
    </UMain>
</template>

<style></style>
