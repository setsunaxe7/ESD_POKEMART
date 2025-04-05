<script setup lang="ts">
    import type { Card } from "~/types/card";
    import { useCards } from "#imports";
    import axios from "axios";
    import type { BreadcrumbItem, TabsItem } from "@nuxt/ui";
    import { USeparator } from "#components";
    const { card, cardLoading, cardError, fetchCard } = useCards();

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

    const items = ref<TabsItem[]>([
        {
            label: "All listings",
            slot: "all",
        },
        {
            label: "Buy Now",
            slot: "direct",
        },
        {
            label: "Auctions",
            slot: "auction",
        },
    ]);

    onMounted(async () => {
        // Fetch card from our database
        await fetchCard(id);

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
                            <template #all="{ item }"></template>
                            <template #direct="{ item }"></template>
                            <template #auction="{ item }"></template>
                        </UTabs>
                    </div>
                </div>
            </div>
        </UContainer>
    </UMain>
</template>
