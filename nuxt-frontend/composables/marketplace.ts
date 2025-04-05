import { ref } from "vue";
import axios from "axios";
import type { Listing } from "~/types/listing";

interface Filters {
    status?: string;
    type?: string;
    seller_id?: string;
    card_id?: string;
}

export function useListings() {
    const listings = ref<Listing[]>([]);
    const isListingLoading = ref(true);
    const listingError = ref<string | null>(null);

    const fetchListings = async (filters: Filters = {}) => {
        try {
            isListingLoading.value = true;

            // Build query parameters from filters object
            const params = new URLSearchParams();

            // Add each filter to the params if it has a value
            if (filters.status) params.append("status", filters.status);
            if (filters.type) params.append("type", filters.type);
            if (filters.seller_id) params.append("seller_id", filters.seller_id);
            if (filters.card_id) params.append("card_id", filters.card_id);

            // Construct URL with query parameters
            const url = `http://127.0.0.1:8000/marketplace/api/marketplace/listings${
                params.toString() ? "?" + params.toString() : ""
            }`;

            console.log(url);

            const response = await axios.get(url);
            listings.value = response.data;
        } catch (err) {
            listingError.value = err.message || "Failed to fetch listings";
            console.error(listingError.value);
        } finally {
            isListingLoading.value = false;
        }
    };

    return {
        listings,
        isListingLoading,
        listingError,
        fetchListings,
    };
}
