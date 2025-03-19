<script setup lang="ts">
    import { useCards } from "../composables/inventory";

    const { cards, isLoading, error, fetchCards } = useCards();

    // Fetch cards when component mounts
    onMounted(fetchCards);
</script>

<template>
    <UContainer
        class="min-h-[calc(100vh-var(--header-height)-var(--footer-height)-6rem)] flex flex-col">
        <h1 class="text-2xl font-bold mb-6">Pokémon Card Collection</h1>

        <!-- Loading state -->
        <div
            v-if="isLoading"
            class="flex-1 flex flex-col gap-4 justify-center items-center animate__animated animate__pulse animate__infinite">
            <img src="../assets/img/loader.svg" alt="Loading" class="w-75 h-auto" />
            <h2 class="text-xl font-bold text-gray-500">Loading...</h2>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="p-4 bg-red-100 text-red-700 rounded">
            {{ error }}
        </div>

        <!-- Cards display -->
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <UCard v-for="card in cards" :key="card.id" class="card-container">
                <img
                    v-if="card.image_url"
                    :src="card.image_url"
                    :alt="card.name"
                    class="w-full h-48 object-contain" />
                <div v-else class="w-full h-48 bg-gray-100 flex items-center justify-center">
                    No Image
                </div>

                <h3 class="mt-2 font-medium text-lg">{{ card.name }}</h3>
            </UCard>
        </div>
    </UContainer>
</template>
