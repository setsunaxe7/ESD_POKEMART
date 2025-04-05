import { ref } from "vue";
import axios from "axios";
import type { Card } from "~/types/card";

export function useCards() {
    const cards = ref<Card[]>([]);
    const card = ref<Card | null>(null);
    const isLoading = ref(true);
    const cardLoading = ref(false);
    const error = ref<string | null>(null);
    const cardError = ref<string | null>(null);

    const fetchCards = async () => {
        try {
            isLoading.value = true;
            const response = await axios.get("http://127.0.0.1:8000/inventory/inventory");
            cards.value = response.data;
        } catch (err: any) {
            error.value = err.message || "Failed to fetch cards";
            console.error(error.value);
        } finally {
            isLoading.value = false;
        }
    };

    // Fetch a specific card by ID
    const fetchCard = async (id: string | number) => {
        try {
            cardLoading.value = true;
            cardError.value = null;

            const response = await axios.get(`http://127.0.0.1:8000/inventory/inventory/${id}`);
            card.value = response.data;

            return response.data;
        } catch (err: any) {
            cardError.value = err.message || `Failed to fetch card with ID: ${id}`;
            console.error(cardError.value);
            card.value = null;

            return null;
        } finally {
            cardLoading.value = false;
        }
    };

    return {
       // All cards
       cards,
       isLoading,
       error,
       fetchCards,

       // Single card
       card,
       cardLoading,
       cardError,
       fetchCard
    };
}
