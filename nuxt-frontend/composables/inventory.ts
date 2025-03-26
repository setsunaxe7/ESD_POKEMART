import { ref } from "vue";
import axios from "axios";
import type { Card } from "~/types/card";

export function useCards() {
    const cards = ref<Card[]>([]);
    const isLoading = ref(true);
    const error = ref<string | null>(null);

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

    return {
        cards,
        isLoading,
        error,
        fetchCards,
    };
}
