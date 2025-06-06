<script setup>
    import { ref, onMounted } from "vue";
    import { useSupabaseClient, useSupabaseUser, useToast } from "#imports";

    // Get Supabase client and user
    const supabase = useSupabaseClient();
    const user = useSupabaseUser();
    const toast = useToast();
    const loading = ref(true);
    const updating = ref(false);
    const displayName = ref("");
    const isButtonPressed = ref(false);
    const saveSuccess = ref(false);

    // Handle button click animation
    const handleButtonClick = () => {
        isButtonPressed.value = true;
        setTimeout(() => {
            isButtonPressed.value = false;
        }, 200);
    };

    // Fetch user data
    const fetchUserData = async () => {
        try {
            loading.value = true;

            if (!user.value) {
                loading.value = false;
                return;
            }

            // Get user data from Supabase
            const { data, error } = await supabase.auth.getUser();

            if (error) {
                throw error;
            }

            if (data && data.user) {
                console.log("User data from Supabase:", data.user);

                // Extract display name from raw_user_meta_data
                if (data.user.user_metadata && data.user.user_metadata.display_name) {
                    displayName.value = data.user.user_metadata.display_name;
                } else {
                    displayName.value = "";
                }
            }
        } catch (error) {
            console.error("Error fetching user data:", error);
            toast.add({
                title: "Error fetching user data",
                description: error.message,
                color: "red",
            });
        } finally {
            loading.value = false;
        }
    };

    // Update display name
    const updateDisplayName = async () => {
        try {
            updating.value = true;
            saveSuccess.value = false;

            if (!user.value) return;

            // Update using Supabase Auth API - specifically targeting the metadata
            const { data, error } = await supabase.auth.updateUser({
                data: {
                    display_name: displayName.value,
                },
            });

            if (error) throw error;

            console.log("Update response:", data);

            // Refresh user data
            await fetchUserData();

            toast.add({
                title: "Display name updated",
                color: "green",
            });

            saveSuccess.value = true;
            setTimeout(() => {
                saveSuccess.value = false;
            }, 3000);
        } catch (error) {
            console.error("Error updating display name:", error);
            toast.add({
                title: "Error updating display name",
                description: error.message,
                color: "red",
            });
        } finally {
            updating.value = false;
        }
    };

    // Load user data when component mounts
    onMounted(() => {
        fetchUserData();
    });
</script>

<template>
    <UMain class="min-h-[calc(100vh-var(--header-height)-var(--footer-height))]">
        <UContainer>
            <div class="p-4">
                <UCard class="max-w-xl mx-auto">
                    <template #header>
                        <h1 class="text-xl font-bold">My Account</h1>
                    </template>

                    <div v-if="loading" class="flex justify-center p-4">
                        <ULoading />
                    </div>

                    <div v-else class="space-y-6">
                        <div class="grid grid-cols-1 gap-4">
                            <!-- User Information -->
                            <div>
                                <h2 class="font-semibold mb-2">Account Information</h2>
                                <div class="grid grid-cols-3 gap-2">
                                    <div class="font-medium">Email:</div>
                                    <div class="col-span-2">{{ user?.email }}</div>

                                    <div class="font-medium">User ID:</div>
                                    <div class="col-span-2 text-sm text-gray-600 truncate">
                                        {{ user?.id }}
                                    </div>

                                    <div class="font-medium">Display Name:</div>
                                    <div class="col-span-2">{{ displayName || "Not set" }}</div>
                                </div>
                            </div>

                            <UDivider />

                            <!-- Update Display Name -->
                            <div>
                                <h2 class="font-semibold mb-2">Update Display Name</h2>
                                <form @submit.prevent="updateDisplayName" class="space-y-4">
                                    <UFormGroup label="Display Name" name="displayName">
                                        <UInput v-model="displayName" placeholder="John Doe" />
                                    </UFormGroup>

                                    <UButton
                                        type="submit"
                                        :loading="updating"
                                        :ui="{
                                            rounded: 'rounded-md',
                                            base: 'transition-all duration-200',
                                        }"
                                        class="relative m-2"
                                        @click="handleButtonClick"
                                        :class="{ 'scale-95': isButtonPressed }">
                                        <span>Save Display Name</span>
                                        <UTransition name="fade">
                                            <UIcon
                                                v-if="saveSuccess"
                                                name="i-heroicons-check-circle"
                                                class="ml-2 text-green-200" />
                                        </UTransition>
                                    </UButton>

                                    <div
                                        v-if="saveSuccess"
                                        class="flex items-center text-green-500 text-sm mt-2">
                                        <UIcon name="i-heroicons-check-circle" class="mr-1" />
                                        Display name saved successfully!
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </UCard>
            </div>
        </UContainer>
    </UMain>
</template>

<style scoped>
    .fade-enter-active,
    .fade-leave-active {
        transition: opacity 0.3s;
    }
    .fade-enter-from,
    .fade-leave-to {
        opacity: 0;
    }
</style>
