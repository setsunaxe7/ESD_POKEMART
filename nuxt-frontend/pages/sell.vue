<script lang="ts" setup>
    import { useCards } from "../composables/inventory";
    import axios from "axios";
    import { ref, computed, onMounted } from "vue";
    const { cards, isLoading, error, fetchCards } = useCards();

    const user = useSupabaseUser();
    const userId: any = user.value?.id;
    const userName: any = user.value?.user_metadata.display_name;

    interface ListingData {
        seller_id: string;
        seller_name: string;
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

    const psaGradeOptions = [
        {
            label: "Ungraded",
            value: 0,
        },
        {
            label: "PSA 1 - Poor",
            value: 1,
        },
        {
            label: "PSA 2 - Fair",
            value: 2,
        },
        {
            label: "PSA 3 - Good",
            value: 3,
        },
        {
            label: "PSA 4 - Very Good",
            value: 4,
        },
        { label: "PSA 5 - Excellent", value: 5 },
        {
            label: "PSA 6 - Excellent-Mint",
            value: 6,
        },
        {
            label: "PSA 7 - Near Mint",
            value: 7,
        },
        {
            label: "PSA 8 - Near Mint-Mint",
            value: 8,
        },
        {
            label: "PSA 9 - Mint",
            value: 9,
        },
        {
            label: "PSA 10 - Gem Mint",
            value: 10,
        },
    ];

    const toast = useToast();
    function showToast() {
        toast.add({
            title: "Success!",
            description: "Your listing has been created",
        });
    }

    const listingType = [
        { label: "Fixed price", value: "direct" },
        { label: "Auction", value: "auction" },
    ];

    // Fetch cards when component mounts
    onMounted(async () => {
        await fetchCards();
        // selectedCard.value = cardOptions.value[0];
    });

    const selectedCard = ref();
    const selectedGrade = ref();
    const description = ref();
    const selectedType = ref("direct");

    const price = ref();
    const startingPrice = ref();
    const auctionDuration = ref();
    const title = ref();

    const durationOptions = [
        { label: "3 days", value: 3 },
        { label: "5 days", value: 5 },
        { label: "7 days", value: 7 },
        { label: "10 days", value: 10 },
    ];

    const cardOptions = computed(() => {
        if (!cards.value) return [];

        return cards.value.map((card) => ({
            label: card.name + " [" + card.rarity + "]",
            value: card.id,
            card: card,
        }));
    });

    const imageFile = ref(null);
    const isSubmitting = ref(false);
    const submissionError = ref("");

    // Handle file selection
    const handleFileChange = (event: any) => {
        imageFile.value = event.target.files[0];
    };

    const createListing = async () => {
        if (!selectedCard.value || !selectedGrade.value) {
            submissionError.value = "Please select a card and grade";
            return;
        }

        if (selectedType.value === "direct" && !price.value) {
            submissionError.value = "Please enter a price";
            return;
        }

        if (selectedType.value === "auction" && (!startingPrice.value || !auctionDuration.value)) {
            submissionError.value = "Please enter starting price and auction duration";
            return;
        }

        isSubmitting.value = true;
        submissionError.value = "";

        try {
            const formData = new FormData();

            // Add image file if selected
            if (imageFile.value) {
                formData.append("image", imageFile.value);
            }

            // Calculate auction dates if needed
            let auctionStartDate, auctionEndDate;
            if (selectedType.value === "auction") {
                auctionStartDate = new Date().toISOString();
                auctionEndDate = new Date();
                auctionEndDate.setDate(auctionEndDate.getDate() + auctionDuration.value.value);
                auctionEndDate = auctionEndDate.toISOString();
            }

            // Create listing data object
            const listingData: ListingData = {
                seller_id: userId, // Replace with actual user ID from auth
                seller_name: userName,
                card_id: selectedCard.value.value,
                title: title.value,
                description: description.value,
                price:
                    selectedType.value === "direct"
                        ? parseFloat(price.value)
                        : parseFloat(startingPrice.value),
                type: selectedType.value,
                status: "active",
                grade: selectedGrade.value.value,
            };

            // Add auction details if applicable
            if (selectedType.value === "auction") {
                listingData.auction_start_date = auctionStartDate;
                listingData.auction_end_date = auctionEndDate;
            }

            // Append the JSON data to the form
            formData.append("data", JSON.stringify(listingData));

            // Send the request
            const response = await axios.post(
                "http://127.0.0.1:8000/marketplace/api/marketplace/listings",
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                }
            );

            // Handle success - redirect or show success message
            console.log("Listing created successfully:", response.data);
        } catch (error: any) {
            console.error("Error creating listing:", error);
            submissionError.value = error.response?.data?.error || "Failed to create listing";
        } finally {
            isSubmitting.value = false;
            showToast();
        }
    };
</script>
<template>
    <UMain>
        <UContainer>
            <UPageSection
                title="Sell Your Cards"
                description="List your Pokémon cards for sale in the marketplace"
                :ui="{ container: 'lg:py-24' }" />
            <Loading v-if="isLoading"></Loading>
            <div v-else class="flex flex-col space-y-8 mb-8">
                <UCard class="p-4">
                    <div class="flex flex-col gap-8">
                        <div class="flex flex-col gap-2">
                            <h1 class="text-2xl font-bold">Card Details</h1>
                            <p class="text-gray-500">Select the card that you want to sell</p>
                        </div>

                        <!-- Card selection and preview section -->
                        <div class="grid grid-cols-3 gap-12">
                            <!-- Card selection -->
                            <div class="col-span-2 flex flex-col justify-between h-96">
                                <div class="flex flex-col gap-3">
                                    <p class="font-medium">Search for your card</p>
                                    <USelectMenu
                                        v-model="selectedCard"
                                        placeholder="Select card"
                                        :items="cardOptions"
                                        class="w-full" />
                                </div>

                                <div class="flex flex-col gap-3">
                                    <p class="font-medium">Card grade</p>
                                    <USelectMenu
                                        v-model="selectedGrade"
                                        placeholder="Select a grade"
                                        :items="psaGradeOptions"
                                        class="w-full" />
                                </div>
                                <div class="flex flex-col gap-3">
                                    <p class="font-medium">Listing Title</p>
                                    <UInput
                                        v-model="title"
                                        placeholder="Add a title for your listing"></UInput>
                                </div>
                                <div class="flex flex-col gap-3">
                                    <p class="font-medium">Card Description (Optional)</p>
                                    <UTextarea
                                        :rows="3"
                                        v-model="description"
                                        variant="outline"
                                        placeholder="Add details about your card, such as any special features or minor flaws" />
                                </div>
                            </div>

                            <!-- Card preview -->
                            <div class="col-span-1 flex justify-end">
                                <div class="w-64 h-96 rounded-lg overflow-hidden">
                                    <div
                                        v-if="!selectedCard"
                                        class="w-full h-full bg-gray-100 flex items-center justify-center text-gray-400">
                                        Card Preview
                                    </div>
                                    <img
                                        v-else
                                        :src="selectedCard.card.image_url"
                                        :alt="selectedCard.card.name"
                                        class="w-full h-full object-fit-contain" />
                                </div>
                            </div>
                        </div>
                    </div>
                </UCard>
                <UCard class="p-4">
                    <div class="flex flex-col gap-2 w-1/2">
                        <h1 class="text-2xl font-bold">Card Image</h1>
                        <p class="text-gray-500">Upload a clear photo of your card</p>
                        <UInput class="mt-2" type="file" @change="handleFileChange"></UInput>
                    </div>
                </UCard>
                <UCard class="p-4">
                    <div class="flex flex-col gap-4">
                        <div class="flex flex-col gap-2">
                            <h1 class="text-2xl font-bold">Listing Details</h1>
                            <p class="text-gray-500">Set your price and listing preferences</p>
                        </div>
                        <div class="flex flex-col gap-2 mt-2">
                            <p class="font-medium">Listing Type</p>
                            <URadioGroup
                                class="mt-2"
                                orientation="horizontal"
                                v-model="selectedType"
                                default-value="direct"
                                :items="listingType"
                                color="neutral" />
                        </div>
                        <div class="flex flex-col gap-4 mt-2">
                            <!-- Direct listing options -->
                            <div v-if="selectedType === 'direct'" class="flex flex-col gap-2 w-1/4">
                                <p class="font-medium">Price</p>
                                <UInput
                                    leading-icon="i-material-symbols:attach-money"
                                    v-model="price"
                                    placeholder="0.00"
                                    type="number" />
                            </div>

                            <!-- Auction listing options -->
                            <div v-else class="flex flex-col gap-4 w-1/4">
                                <div class="flex flex-col gap-2">
                                    <p class="font-medium">Starting Price</p>
                                    <UInput
                                        v-model="startingPrice"
                                        leading-icon="i-material-symbols:attach-money"
                                        type="number"
                                        placeholder="0.00" />
                                </div>

                                <div class="flex flex-col gap-2">
                                    <p class="font-medium">Auction Duration</p>
                                    <USelectMenu
                                        v-model="auctionDuration"
                                        placeholder="Select a duration"
                                        :items="durationOptions"
                                        class="w-full" />
                                </div>
                            </div>
                        </div>
                    </div>
                </UCard>
                <UButton
                    size="xl"
                    :block="true"
                    class="w-1/2 m-auto"
                    @click="createListing"
                    :loading="isSubmitting"
                    :disabled="isSubmitting">
                    Create Listing
                </UButton>
            </div>
        </UContainer>
    </UMain>
</template>
