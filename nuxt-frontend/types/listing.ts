export interface Listing {
    id: string;
    seller_id: string;
    card_id: string;
    title: string;
    description: string;
    price: number;
    type: "direct" | "auction";
    status: "active" | "sold" | "cancelled";
    grade: number;
    image_url: string;
    created_at: string;
    updated_at: string;
    seller_name: string;

    // Auction specific properties
    auction_start_date?: string | null;
    auction_end_date?: string | null;
    highest_bid?: number | null;
    highest_bidder_id?: string | null;
    bid_count?: number;
    reserve_price?: number | null;
}
