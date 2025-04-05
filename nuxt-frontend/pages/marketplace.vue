<script setup lang="ts">

import { ref, onMounted, onUnmounted } from "vue";
import type { Listing } from "../types/listing";
import { UButton } from "#components";
import WebSocketService from "../services/websocketService.js";

// Reactive variables for search, sorting, and pagination
const searchQuery = ref("");
const sortBy = ref("Relevance");
const currentPage = ref(1);

const listings = ref<Listing[]>([]);

// Fetch Cards from API and set up WebSocket
onMounted(async () => {
  try {
    const response = await $fetch<Listing[]>("http://localhost:8000/marketplace/api/marketplace/listings");
    listings.value = response; // Assign API response to listings

    // Subscribe to auction updates via WebSocket
    WebSocketService.econnect("ws://localhost:15674/ws",  "grading_topic", "*.auction", (message) => {
      const { listing_id, highest_bid } = message; // Destructure the message object

      // Find the index of the relevant listing in the listings array
      const index = listings.value.findIndex(
          (listing) => listing.id === listing_id && listing.type === "auction"
        );

        if (index !== -1) {
          // Replace the entire object at the found index to trigger reactivity
          listings.value[index] = {
            ...listings.value[index], // Keep other properties unchanged
            highest_bid,              // Update the highest_bid property
          };
          console.log(`Updated highest bid for listing ${listing_id}: ${highest_bid}`);
        }

    });

  } catch (error) {
    console.error("Error fetching marketplace listings:", error);
  }
});

// Disconnect WebSocket on component unmount
onUnmounted(() => {
  WebSocketService.disconnect();
});

// Dropdown menu items for sorting
const items = ref([
  {
    label: "Relevance",
    icon: "i-lucide-user",
  },
  {
    label: "In Stock",
    icon: "i-lucide-user",
  },
  {
    label: "Grade",
    icon: "i-lucide-user",
  },
  {
    label: "Sort: A to Z",
    icon: "i-lucide-user",
  },
  {
    label: "Sort: Z to A",
    icon: "i-lucide-user",
  },
  {
    label: "$: Low to High",
    icon: "i-lucide-credit-card",
  },
  {
    label: "$: High to Low",
    icon: "i-lucide-cog",
  },
]);

</script>


<template>
    <UMain>
      <div class="flex h-screen">
        <!-- Sidebar -->
        <div
          class="hidden md:block w-40 h-full flex-shrink-0"
        >

        <!-- Sidebar -->
          <div class="flex items-center gap-2 px-4 py-2">
            <span class="font-bold text-lg">Filter</span>
          </div>

          <UNavigationMenu
            :items="items"
            :content="{
              align: 'start',
              side: 'bottom',
              sideOffset: 8
            }"
            :ui="{
              content: 'w-70'
            }"
            orientation = "vertical"
            class = "mt-auto"
          >
          </UNavigationMenu>

        </div>

        <!-- Main Content -->
        <UContainer class="flex-grow p-4 overflow-y-auto">
          <USlideover
          side="left"
          title="Filters"
        >
          <UButton label="Filters" color="neutral" variant="subtle" class="block md:hidden"/>
          <template #body>
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
          </template>
        </USlideover>
          <!-- Search Input -->
          <UInput
            v-model="searchQuery"
            placeholder="Search Pokemon cards..."
            icon="i-heroicons-magnifying-glass"
            class="w-full max-w mb-4"
          />

          <!-- Marketplace Listings -->
          <UPageGrid>
            <!-- Dynamically create cards for each listing -->
            <UPageCard v-for="listing in listings" :key="listing.id">
              <NuxtLink :to="'/listing/' + listing.id">
                <img
                  :src="listing.image_url || 'https://placehold.co/400'"
                  alt="listing.title"
                  class="w-full h-40 object-cover"
                  loading="lazy"
                />
                <h3 class="text-lg font-medium mt-2">{{ listing.title }}</h3>
                <p class="text-sm text-gray-500">{{ listing.description }}</p>
                <p class="text-primary font-bold"> 
                  {{
                    listing.type === 'auction'
                      ? new Intl.NumberFormat("en-US", {
                          style: "currency",
                          currency: "USD",
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        }).format(listing.highest_bid || 0)
                      : new Intl.NumberFormat("en-US", {
                          style: "currency",
                          currency: "USD",
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        }).format(listing.price || 0)
                  }}
                </p>
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
