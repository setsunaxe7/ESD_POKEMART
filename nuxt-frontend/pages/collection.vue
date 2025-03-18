<script setup lang="ts">
    import axios from "axios";

    // Define interfaces for type safety
    interface PokemonCardImage {
        small: string;
        large: string;
    }

    interface PokemonCard {
        id: string;
        name: string;
        images: PokemonCardImage;
        // Add other properties you need
    }

    interface PokemonApiResponse {
        data: PokemonCard[];
    }

    // State for cards
    const cards = ref<PokemonCard[]>([]);
    const isLoading = ref(true);
    const error = ref<string | null>(null);

    // Function to fetch cards
    const fetchCards = async () => {
        try {
            isLoading.value = true;
            const response = await axios.get<PokemonApiResponse>(
                "https://api.pokemontcg.io/v2/cards?q=set.id:sv3",
                {
                    headers: {
                        "X-Api-Key": "1bdbe362-1c4f-47bf-9f67-c5553234c826",
                    },
                }
            );

            cards.value = response.data.data;
            console.log("Cards loaded:", cards.value.length);
        } catch (err: any) {
            error.value = err.message || "Failed to fetch Pokemon cards";
            console.error(error.value);
        } finally {
            isLoading.value = false;
        }
    };

    // Call the fetch function when component mounts
    onMounted(fetchCards);
</script>

<template>
    <UMain>
        <UContainer>
            <h1 class="text-2xl font-bold mb-6">Pokémon Card Collection</h1>

            <div v-if="isLoading" class="flex justify-center my-8">
                <ULoading />
            </div>

            <div v-else-if="error" class="text-red-500">
                {{ error }}
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                <div v-for="card in cards" :key="card.id" class="card-container">
                    <img :src="card.images.small" :alt="card.name" class="w-full rounded" />
                    <p class="mt-2 font-medium">{{ card.name }}</p>
                </div>
            </div>
        </UContainer>
    </UMain>
</template>
