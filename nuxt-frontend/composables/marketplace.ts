import { ref } from "vue";
import axios from "axios";

interface ListingData {
    seller_id: string;
    card_id: number;
    title: string;
    description: string;
    price: number;
    type: string;
    status: string;
    grade: number;
    auction_start_date?: string; // Optional property
    auction_end_date?: string; // Optional property
}

export function useListings() {
    const listings = ref<ListingData[]>([]);
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
