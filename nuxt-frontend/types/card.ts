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
