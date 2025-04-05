<script setup lang="ts">
    import { useCards } from "#imports";
    import { CardDetail } from "#components";
    const { cards, isLoading, error, fetchCards } = useCards();

    const itemsPerPage = 12;
    const route = useRoute();

    const currentPage = computed(() => {
        const pageParam = route.params.page;
        const pageNumber = pageParam ? parseInt(pageParam as string) : 1;
        return isNaN(pageNumber) || pageNumber < 1 ? 1 : pageNumber;
    });

    // Calculate paginated cards based on current page
    const paginatedCards = computed(() => {
        if (!cards.value || !cards.value.length) return [];

        const startIndex = (currentPage.value - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;

        return cards.value.slice(startIndex, endIndex);
    });

    // Fetch cards when component mounts
    onMounted(fetchCards);
</script>

<template>
    <UContainer class="min-h-[calc(100vh-var(--header-height)-var(--footer-height))] flex flex-col">
        <UPageSection
            title="Featured Card Collection"
            description="View all the cards in the iconic Scarlet & Violet 151 collection"
            :ui="{ container: 'lg:py-24' }" />

        <!-- Loading state -->
        <Loading v-if="isLoading"></Loading>

        <!-- Error state -->
        <div v-else-if="error" class="p-4 bg-red-100 text-red-700 rounded">
            {{ error }}
        </div>

        <!-- Cards display -->
        <div v-else>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-16">
                <CardDetail v-for="card in paginatedCards" :key="card.id" :card="card" />
            </div>
            <div class="my-16 flex justify-center">
                <UPagination
                    v-model:page="currentPage"
                    size="lg"
                    :to="(page) => ({ path: `/collection/page/${page}` })"
                    :items-per-page="itemsPerPage"
                    :total="cards.length" />
            </div>
        </div>
    </UContainer>
</template>
