<script setup lang="ts">

const searchQuery = ref("");
const sortBy = ref("Relevance");
const currentPage=ref(1);

// Fetch Cards (pending API endpoint, trial code)
const { data: cards } = await useAsyncData(() =>
    $fetch(`/api/cards`, {
        query: { page: currentPage.value, search: searchQuery.value, sort: sortBy.value },
    })
);

const items = ref([
  {
    label: 'Relevance',
    icon: 'i-lucide-user'
  },
  {
    label: 'Price: Low to High',
    icon: 'i-lucide-credit-card'
  },
  {
    label: 'Price: High to Low',
    icon: 'i-lucide-cog'
  }
])
</script>

<template>
    <UMain>
        <UContainer>
            <h1>Marketplace Page</h1>
            <div class="p-4">

                <UInput v-model="searchQuery" placeholder="Search Pokemon cards..." icon="i-heroicons-magnifying-glass" class="w-full max-w" />

                <UDropdownMenu
                    :items="items"
                    :content="{
                    align: 'start',
                    side: 'bottom',
                    sideOffset: 8
                    }"
                    :ui="{
                    content: 'w-48'
                    }"
                >
                    <UButton label="Open" icon="i-lucide-menu" color="neutral" variant="outline" />
                </UDropdownMenu>

                <UPageGrid>
                    <UPageCard v-for="card in cards" :key="card.id">
                        <NuxtLink :to="`/product/${card.id}`">
                        <img :src="card.image" alt="card.name" class="w-full h-40 object-cover" loading="lazy" />
                        <h3 class="text-lg font-medium mt-2">{{ card.name }}</h3>
                        <p class="text-sm text-gray-500">{{ card.set }}</p>
                        <p class="text-primary font-bold">${{ card.price }}</p>
                        </NuxtLink>
                    </UPageCard>
                </UPageGrid>

                <UPagination v-model="currentPage" :total="100" :per-page="20" class="mt-6 justify-between items-center" />

            </div>
        </UContainer>
    </UMain>
</template>