<script setup lang="ts">
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
</script>
<template>
    <UMain>
        <UContainer>
            <UPageSection
                title="Professional Card Grading"
                description="Get your valuable Pokémon cards authenticated and graded by experts"
                :ui="{container: 'lg:py-24'}" />
            <UTabs
                color="primary"
                size="xl"
                variant="link"
                :items="items"
                class="w-full"
                :ui="{ trigger: 'flex-1' }" />
        </UContainer>
    </UMain>
</template>
