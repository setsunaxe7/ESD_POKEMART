<script setup lang="ts">
    import type { Card } from "../types/card";
    import { useRouter } from "vue-router";

    // Get router instance
    const router = useRouter();

    // Function to navigate to card detail page
    const navigateToCard = () => {
        router.push(`/card/${props.card.id}`);
    };

    // Define the prop for the card
    const props = defineProps<{
        card: Card;
    }>();
</script>

<template>
    <div
        class="card-detail relative overflow-hidden rounded-lg transition-all duration-200 group"
        @click="navigateToCard">
        <!-- Card Image -->
        <img
            :src="card.image_url || 'https://placehold.co/300x400/f3f4f6/d1d5db?text=No+Image'"
            :alt="card.name"
            class="w-full h-full" />

        <!-- Hover Information Overlay -->
        <div
            class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-3">
            <h3 class="text-white font-bold text-lg line-clamp-2">{{ card.name }}</h3>
            <p v-if="card.rarity" class="text-green-400 font-bold text-sm">{{ card.rarity }}</p>
        </div>
    </div>
</template>

<style scoped>
    .card-detail {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    .card-detail:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        transform: translateY(-4px);
        cursor: pointer;
    }
</style>
