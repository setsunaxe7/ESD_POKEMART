import { ref } from "vue";
import axios from "axios";

export interface Card {
    id: number;
    card_id: string;
    name: string;
    image_url?: string;
    high_res_image?: string;
    set_id: string;
    created_at: Date;
    rarity?: string;
}

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
