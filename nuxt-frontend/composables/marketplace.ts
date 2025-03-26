import { ref } from "vue";
import axios from "axios";
import type { Listing } from "~/types/listing";

export function useListings() {
    const listings = ref<Listing[]>([]);
    const isListingLoading = ref(true);
    const listingError = ref<string | null>(null);

    const fetchListings = async () => {
        try {
            isListingLoading.value = true;
            const response = await axios.get("http://127.0.0.1:8001/api/marketplace/listings");
            listings.value = response.data;
        } catch (err: any) {
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
