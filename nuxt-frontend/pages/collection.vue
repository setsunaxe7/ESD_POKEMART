<script setup lang="ts">
    import { useCards } from "../composables/inventory";

    const { cards, isLoading, error, fetchCards } = useCards();

    // Fetch cards when component mounts
    onMounted(fetchCards);
</script>

<template>
    <UContainer
        class="min-h-[calc(100vh-var(--header-height)-var(--footer-height))] flex flex-col">
        <UPageSection
                title="Featured Card Collection"
                description="View all the cards in the iconic Scarlet & Violet 151 collection"
                :ui="{container: 'lg:py-24'}" />

        <!-- Loading state -->
        <Loading v-if="isLoading"></Loading>

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
