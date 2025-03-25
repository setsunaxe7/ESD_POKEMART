<script setup lang="ts">
import { useListings } from "../composables/marketplace";

const { listings, isListingLoading, listingError, fetchListings } = useListings();

onMounted(fetchListings);

// const searchQuery = ref("");
// const sortBy = ref("Relevance");
// const currentPage=ref(1);

// // Fetch Cards (pending API endpoint, trial code)
// const { data: listings } = await useAsyncData(() =>
//     $fetch(`127.0.0.1:8001/api/marketplace/listings`, {
//         // query: { page: currentPage.value, search: searchQuery.value, sort: sortBy.value },
//     })
// );

console.log(listings)

// edit to see how to implement the same fetching data in marketplace/inventory.ts

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
            <div>

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

                <UDashboardSidebar resizable collapsible>
                    <div class="flex items-center gap-2 px-4 py-2">
                        <span class="font-bold text-lg">Menu</span>
                    </div>
                    <ul class="flex flex-col gap-2">
                        <li class="px-4 py-2 hover:bg-gray-100 rounded">Option 1</li>
                        <li class="px-4 py-2 hover:bg-gray-100 rounded">Option 2</li>
                        <li class="px-4 py-2 hover:bg-gray-100 rounded">Option 3</li>
                    </ul>
                    <div class="flex items-center gap-2 px-4 py-2">
                        <span>Footer Content</span>
                    </div>
                </UDashboardSidebar>

                <UPageGrid>
                    <!-- <UPageCard v-for="card in cards" :key="card.id"> -->
                        <!-- <NuxtLink :to="`/product/${card.id}`">
                        <img :src="card.image" alt="card.name" class="w-full h-40 object-cover" loading="lazy" />
                        <h3 class="text-lg font-medium mt-2">{{ card.name }}</h3>
                        <p class="text-sm text-gray-500">{{ card.set }}</p>
                        <p class="text-primary font-bold">${{ card.price }}</p> -->
                        <!-- </NuxtLink> -->
                    <UPageCard>
                        <p class="text-primary font-bold">Hello</p>
                    </UPageCard>
                </UPageGrid>

                <div class="flex justify-center">
                    <UPagination v-model="currentPage" :total="100" :per-page="20" class="mt-6 justify-between items-center" />
                </div>

            </div>
        </UContainer>
    </UMain>
</template>