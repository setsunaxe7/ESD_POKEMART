<script setup lang="ts">
    import { ref, watch, onMounted } from 'vue';
    import { useCards } from "../composables/inventory";

    // Get card info from Inventory ms
    const { cards, isLoading, error, fetchCards } = useCards();
    onMounted(fetchCards);

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

    // CardNameArr
    const cardName = ref([]);

    // Form input variables
    const cardId = ref<string | undefined>(undefined);

    // Filling up CardNameArr
    watch(cards, (newCards) => {
        if (newCards && newCards.length > 0) {
            cardName.value = newCards.map(card => ({
                label: card.name,
                slot: card.card_id, 
            }));

            cardId.value = newCards[0].card_id;
        }
    });

    // Form input variables
    const address = ref("");
    const postalCode = ref("");

    // errorMsg variables
    const isWrongInput = ref(false);
    const errMsg = ref("");

    // Submit form/ integration w backend
    function submitForm() {
        if(!address.value.trim() && !postalCode.value.trim()){
            errMsg.value = "Please enter your address & postal code.";
            isWrongInput.value = true;
            console.log("works");
            return;
        }
        if(!address.value.trim()){
            errMsg.value = "Please enter your address.";
            isWrongInput.value = true;
            console.log("works");
            return;
        }
        if(postalCode.value.toString().length == 0){
            errMsg.value = "Please enter your postal code.";
            isWrongInput.value = true;
            console.log("works");
            return;
        }
        if(postalCode.value.toString().length > 6){
            errMsg.value = "Postal Code is over 6 characters";
            isWrongInput.value = true;
            console.log("works");
            return;
        }
        console.log(postalCode.value);
        console.log(address.value);
        address.value = "";
        postalCode.value = "";
        isWrongInput.value = false;
        errMsg.value = "";
        return;
    }

    // Change Date from Inventory ms into Date String
    function formatDate(date: Date | string): string {
    if (typeof date === 'string') {
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
    <UContainer>
        <!-- Top header -->
        <UPageSection
            title="Professional Card Grading"
            description="Get your valuable Pokémon cards authenticated and graded by experts"
            :ui="{container: 'lg:py-24'}" />

        <!-- Submit Request/ My Request tabs -->
        <UTabs
            color="primary"
            size="xl"
            variant="link"
            :items="items"
            class="w-full"
            :ui="{ trigger: 'flex-1' }" 
        >

        <!-- Submit Request content -->
            <template #submit>
                <!-- Error Message -->
                <div v-if="isWrongInput">
                    <UAlert 
                        :title="errMsg"
                        color="error"
                        variant="subtle"
                        icon="material-symbols:warning"
                    />
                    <br>
                </div>
                <!-- Form -->
                <UFormField label="Card ID">
                    <USelect 
                        v-model="cardId" 
                        value-key="slot" 
                        :items="cardName" 
                        class="w-full" 
                        required
                    />
                </UFormField>
                <br>
                <UFormField label="Address">
                    <UInput 
                        v-model="address" 
                        placeholder="Enter your address" 
                        class="w-full"
                    />
                </UFormField>
                <br>
                <UFormField label="Postal Code">
                    <UInput 
                        v-model="postalCode"  
                        type="number"
                        placeholder="Enter your postal code" 
                        class="w-full"
                        style="
                            -webkit-appearance: none; 
                            -moz-appearance: textfield; 
                            appearance: none;"
                    />
                </UFormField>
                <br>
                <UButton @click="submitForm">Submit</UButton>
            </template>

            <!-- My Request content -->
            <template #requests>  
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Each Card -->
                    <UCard v-for="card in cards" :key="card.id" class="card-container flex items-center">
                        <div class="grid grid-cols-3 gap-4 max-w-100">
                            <div class="col-span-1">
                                <img
                                v-if="card.image_url"
                                :src="card.image_url"
                                :alt="card.name"
                                class="w-full h-auto object-contain"
                                />
                                <div v-else class="w-full h-auto bg-gray-100 flex items-center justify-center">
                                No Image
                                </div>
                            </div>

                            <!-- Text within the Card -->
                            <div class="col-span-2 content-evenly">
                                <h3 class="font-medium text-lg">{{ card.name }}</h3>
                                <p class="text-gray-600">Rarity: {{ card.rarity || "Unknown" }}</p>
                                <p class="text-gray-600">Submitted At: {{ formatDate(card.created_at) }}</p>
                                <p class="text-gray-600">Status: 
                                    <UBadge label="Submitted"/>
                                </p>
                                <p v-if="true" class="text-gray-600">Result: -</p>
                            </div>
                        </div>
                    </UCard>
                </div>
            </template>
        </UTabs>
    </UContainer>
</UMain>
</template>
