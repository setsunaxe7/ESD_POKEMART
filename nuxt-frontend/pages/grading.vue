<script setup lang="ts">
    import { ref, onMounted, computed, onUnmounted } from "vue";
    import { useCards } from "../composables/inventory";
    import { useSupabaseClient, useSupabaseUser } from "#imports";

    // supabase module
    import SupabaseUserService from "../services/supabaseUserService.js";

    // websocket module
    import WebSocketService from "../services/websocketService.js";

    // Get card info from Inventory ms
    const { cards, error, fetchCards } = useCards();

    const isLoading = ref(true);

    // CardName
    const cardName = computed(() => {
        if (!cards.value) return [];

        return cards.value.map((card) => ({
            label: card.name + " [" + card.rarity + "]",
            value: card.card_id,
        }));
    });

    // CardMap
    const cardMap = computed(() => {
        if (!cards.value) return {};

        return cards.value.reduce((acc, card) => {
            acc[card.card_id] = {
                name: card.name,
                rarity: card.rarity,
                image_url: card.image_url,
            };
            return acc;
        }, {});
    });

    // Mounted
    onMounted(async () => {
        try {
            // Get cards from inventory for card name dropdown
            await fetchCards();
            cardId.value = cardName.value[0].value;

            // connect to RabbitMQ
            WebSocketService.connect("ws://localhost:15674/ws", "return", onMessageReceived);

            // get UserId
            getUserId();
        } catch (error) {
            console.error("Error fetching marketplace listings:", error);
        } finally {
            isLoading.value = false;
        }
    });

    onUnmounted(() => {
        WebSocketService.disconnect();
    });

    // Tabs items
    const items = [
        {
            label: "Submit Request",
            slot: "submit",
        },
        {
            label: "My Request",
            slot: "requests",
        },
    ];

    //  -------------------------------------------------------------

    // Form input variables
    const cardId = ref("");

    // Form input variables
    const address = ref("");
    const postalCode = ref("");

    // errorMsg variables
    const isWrongInput = ref(false);
    const errMsg = ref("");

    const isSuccess = ref(false);
    const successMsg = ref("");

    //  -------------------------------------------------------------

    // RabbitMQ functions
    const exchange = "grading_topic";

    // Receive Message function
    const userRequests = ref("");
    const onMessageReceived = (msg) => {
        console.log("Received:", msg);
        userRequests.value = msg;
    };
    // Send message function
    const sendMessage = (routingKey, jsonStr) => {
        WebSocketService.sendMessage(exchange, routingKey, jsonStr);
    };

    //  -------------------------------------------------------------

    // Supabase User
    const supabaseClient = useSupabaseClient();
    const user = useSupabaseUser();

    // Initialize the user service
    const userService = new SupabaseUserService(supabaseClient);

    // Get user id
    const uuid = ref("");

    // Get UserId
    const getUserId = async () => {
        const userData = await userService.fetchUserData(user.value);
        if (userData) {
            uuid.value = userData.id;
        }
    };

    //  -------------------------------------------------------------
    // get user's database
    const callDB = (selectedTabKey) => {
        console.log("call db pls");
        if (selectedTabKey) {
            const jsonStr = { userID: uuid.value };
            sendMessage("get.grading", jsonStr);
        }
    };

    // Submit form/ integration w backend
    function submitForm() {
        isSuccess.value = false;
        successMsg.value = "";
        if (!address.value.trim() && !postalCode.value.trim()) {
            errMsg.value = "Please enter your address & postal code.";
            isWrongInput.value = true;
            console.log("works");
            return;
        }
        if (!address.value.trim()) {
            errMsg.value = "Please enter your address.";
            isWrongInput.value = true;
            console.log("works");
            return;
        }
        if (postalCode.value.toString().length == 0) {
            errMsg.value = "Please enter your postal code.";
            isWrongInput.value = true;
            console.log("works");
            return;
        }
        if (postalCode.value.toString().length > 6) {
            errMsg.value = "Postal Code is over 6 characters";
            isWrongInput.value = true;
            console.log("works");
            return;
        }
        const jsonStr = {
            address: address.value,
            cardName: cardMap.value[cardId.value].name,
            cardID: cardId.value,
            postalCode: postalCode.value,
            userID: uuid.value,
        };
        sendMessage("create.grading", jsonStr);
        address.value = "";
        postalCode.value = "";
        isWrongInput.value = false;
        errMsg.value = "";
        isSuccess.value = true;
        successMsg.value = "Request has been submitted";
        return;
    }

    //  -------------------------------------------------------------
    // Change Date from Inventory ms into Date String
    function formatDate(date: Date | string): string {
        if (typeof date === "string") {
            date = new Date(date);
        }
        if (date instanceof Date && !isNaN(date.getTime())) {
            return date.toDateString();
        }
        return "Invalid Date";
    }
</script>

<template>
    <UMain>
        <UContainer class="grading-page">
            <!-- Top header -->
            <UPageSection
                title="Professional Card Grading"
                description="Get your valuable Pokémon cards authenticated and graded by experts"
                :ui="{ container: 'lg:py-24' }" />
            <Loading v-if="isLoading"></Loading>

            <div v-else>
                <!-- Submit Request/ My Request tabs -->
                <UTabs
                    color="primary"
                    size="xl"
                    variant="link"
                    :items="items"
                    class="w-full"
                    :ui="{ trigger: 'flex-1' }"
                    @update:modelValue="callDB">
                    <!-- Submit Request content -->
                    <template #submit>
                        <UCard class="mt-4 p-4">
                            <h1 class="text-2xl font-bold">Grading Form</h1>
                            <USeparator class="my-4"></USeparator>
                            <div class="grid grid-cols-1 md:grid-cols-4 gap-12 mt-6">
                                <div class="col-span-1">
                                    <!-- Card Image -->
                                    <img
                                        v-if="cardId"
                                        :src="cardMap[cardId].image_url"
                                        :alt="cardMap[cardId].name"
                                        class="w-full h-auto object-contain" />
                                </div>
                                <div class="col-span-3">
                                    <!-- Error Message -->
                                    <div v-if="isWrongInput">
                                        <UAlert
                                            :title="errMsg"
                                            color="error"
                                            variant="subtle"
                                            icon="material-symbols:warning" />
                                        <br />
                                    </div>
                                    <!-- Success Message -->
                                    <div v-if="isSuccess">
                                        <UAlert
                                            :title="successMsg"
                                            color="success"
                                            variant="subtle"
                                            icon="formkit:check" />
                                        <br />
                                    </div>
                                    <!-- Form -->
                                    <UFormField label="Card ID">
                                        <USelectMenu
                                            v-model="cardId"
                                            value-key="value"
                                            :items="cardName"
                                            class="w-full" />
                                    </UFormField>
                                    <br />
                                    <UFormField label="Address">
                                        <UInput
                                            v-model="address"
                                            placeholder="Enter your address"
                                            class="w-full" />
                                    </UFormField>
                                    <br />
                                    <UFormField label="Postal Code">
                                        <UInput
                                            v-model="postalCode"
                                            type="number"
                                            placeholder="Enter your postal code"
                                            class="w-full" />
                                    </UFormField>
                                    <br />

                                    <UButton @click="submitForm">Submit</UButton>
                                </div>
                            </div>
                        </UCard>
                    </template>

                    <!-- My Request content -->
                    <template #requests>
                        <div
                            v-if="userRequests.length"
                            class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                            <!-- Each Card -->
                            <UCard
                                v-for="request in userRequests"
                                :key="request.gradingID"
                                class="card-container flex items-center">
                                <div class="grid grid-cols-3 gap-4 max-w-100">
                                    <!-- Card Image -->
                                    <div class="col-span-1">
                                        <img
                                            v-if="cardMap[request.cardID].image_url"
                                            :src="cardMap[request.cardID].image_url"
                                            :alt="cardMap[request.cardID].name"
                                            class="w-full h-auto object-contain" />
                                        <div
                                            v-else
                                            class="w-full h-auto bg-gray-100 flex items-center justify-center">
                                            No Image
                                        </div>
                                    </div>

                                    <!-- Text within the Card -->
                                    <div class="col-span-2 content-evenly">
                                        <h3 class="font-medium text-lg">
                                            {{ cardMap[request.cardID].name }}
                                        </h3>
                                        <p class="text-gray-600">
                                            Rarity:
                                            {{ cardMap[request.cardID].rarity || "Unknown" }}
                                        </p>
                                        <p class="text-gray-600">
                                            Submitted At: {{ formatDate(request.created_at) }}
                                        </p>
                                        <p class="text-gray-600">
                                            Status:
                                            <UBadge
                                                :label="request.status"
                                                :color="
                                                    request.status === 'Created'
                                                        ? 'info'
                                                        : request.status === 'In Progress'
                                                        ? 'warning'
                                                        : request.status === 'Graded'
                                                        ? 'success'
                                                        : 'error'
                                                " />
                                        </p>
                                        <p v-if="request.status == 'Graded'" class="text-gray-600">
                                            Result: {{ request.result }}
                                        </p>
                                    </div>
                                </div>
                            </UCard>
                        </div>
                        <div v-else class="py-16 flex flex-col items-center justify-center">
                            <div class="bg-gray-50 rounded-full p-6 mb-4">
                                <UIcon
                                    name="i-lucide-clipboard-x"
                                    class="w-12 h-12 text-gray-300" />
                            </div>
                            <h3 class="text-xl font-medium text-gray-700 mb-2">
                                No Grading Requests Found
                            </h3>
                            <p class="text-gray-500 text-center max-w-md mb-6">
                                You haven't submitted any card grading requests yet. Start by
                                selecting a card and submitting a grading request.
                            </p>
                        </div>
                    </template>
                </UTabs>
            </div>
        </UContainer>
    </UMain>
</template>

<style scoped>
    /* Remove number input arrows ONLY for this page */
    .grading-page :deep(input[type="number"])::-webkit-outer-spin-button,
    .grading-page :deep(input[type="number"])::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }

    .grading-page :deep(input[type="number"]) {
        -moz-appearance: textfield;
    }
</style>
