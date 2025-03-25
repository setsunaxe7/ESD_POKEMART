<script setup lang="ts">
import { ref, onMounted } from "vue";

// Reactive variables for search, sorting, and pagination
const searchQuery = ref("");
const sortBy = ref("Relevance");
const currentPage = ref(1);

// Reactive variable to hold listings
interface Listing {
  auction_end_date: string | null;
  auction_start_date: string | null;
  bid_count: number;
  card_id: string;
  created_at: string;
  description: string;
  grade: number;
  highest_bid: number | null;
  highest_bidder_id: string | null;
  id: string;
  image_url: string | null;
  price: number;
  reserve_price: number | null;
  seller_id: string;
  status: string;
  title: string;
  type: string;
  updated_at: string;
}

const listings = ref<Listing[]>([]);


// Fetch Cards from API
onMounted(async () => {
  try {
    const response = await $fetch<Listing[]>("http://localhost:5004/api/marketplace/listings");
    listings.value = response; // Assign API response to listings
  } catch (error) {
    console.error("Error fetching marketplace listings:", error);
  }
});

// Dropdown menu items for sorting
const items = ref([
  {
    label: "Relevance",
    icon: "i-lucide-user",
  },
  {
    label: "Price: Low to High",
    icon: "i-lucide-credit-card",
  },
  {
    label: "Price: High to Low",
    icon: "i-lucide-cog",
  },
]);

// WebSocket setup to listen for price updates
onMounted(() => {
  const socket = new WebSocket("ws://localhost:8765");

  socket.onmessage = (event) => {
    const data = event.data.split(":");
    const cardId = data[0];
    const newPrice = data[1];

    // Find the card in the list and update its price dynamically
    const cardToUpdate = listings.value.find((card) => card.id === cardId);
    if (cardToUpdate) {
      cardToUpdate.price = parseFloat(newPrice);
    }
  };

  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
  };
});
</script>

<template>
    <UMain>
      <div class="flex h-screen">
        <!-- Sidebar -->
        <UDashboardSidebar
          resizable
          collapsible
          class="w-1/4 bg-gray-100 h-full flex-shrink-0"
        >
          <div class="flex items-center gap-2 px-4 py-2">
            <span class="font-bold text-lg">Menu</span>
          </div>
          <ul class="flex flex-col gap-2">
            <li class="px-4 py-2 hover:bg-gray-200 rounded">Option 1</li>
            <li class="px-4 py-2 hover:bg-gray-200 rounded">Option 2</li>
            <li class="px-4 py-2 hover:bg-gray-200 rounded">Option 3</li>
          </ul>
          <div class="flex items-center gap-2 px-4 py-2">
            <span>Footer Content</span>
          </div>
        </UDashboardSidebar>
  
        <!-- Main Content -->
        <UContainer class="flex-grow p-4 overflow-y-auto">
          <!-- Search Input -->
          <UInput
            v-model="searchQuery"
            placeholder="Search Pokemon cards..."
            icon="i-heroicons-magnifying-glass"
            class="w-full max-w mb-4"
          />
  
          <!-- Dropdown Menu -->
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
            <UButton
              label="Open"
              icon="i-lucide-menu"
              color="neutral"
              variant="outline"
              class="mb-4"
            />
          </UDropdownMenu>
  
          <!-- Marketplace Listings -->
          <UPageGrid>
            <!-- Dynamically create cards for each listing -->
            <UPageCard v-for="listing in listings" :key="listing.id">
              <NuxtLink :to="'/product/' + listing.id">
                <img
                  :src="listing.image_url || 'https://placehold.co/400'"
                  alt="listing.title"
                  class="w-full h-40 object-cover"
                  loading="lazy"
                />
                <h3 class="text-lg font-medium mt-2">{{ listing.title }}</h3>
                <p class="text-sm text-gray-500">{{ listing.description }}</p>
                <p class="text-primary font-bold">${{ listing.price }}</p>
              </NuxtLink>
            </UPageCard>
          </UPageGrid>
  
          <!-- Pagination -->
          <div class="flex justify-center mt-6">
            <UPagination
              v-model="currentPage"
              :total="100"
              :per-page="20"
              class="justify-between items-center"
            />
          </div>
        </UContainer>
      </div>
    </UMain>
  </template>
  
