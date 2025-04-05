<script setup lang="ts">
    const items = [
        {
            label: "View Collection",
            to: "/collection/page/1",
        },
        {
            label: "Buy Cards",
            to: "/marketplace",
        },
        {
            label: "List Cards",
            to: "/sell",
        },
        {
            label: "Grading Service",
            to: "/grading",
        },
    ];
</script>

<template>
    <UFooter>
        <template #left>
            <p class="text-(--ui-text-muted) text-sm">Copyright © {{ new Date().getFullYear() }}</p>
        </template>

        <UNavigationMenu :items="items" variant="link" />

        <!-- <template #right>
            <UButton
                icon="i-simple-icons-discord"
                color="neutral"
                variant="ghost"
                to="https://chat.nuxt.dev"
                target="_blank"
                aria-label="Discord" />
            <UButton
                icon="i-simple-icons-x"
                color="neutral"
                variant="ghost"
                to="https://x.com/nuxt_js"
                target="_blank"
                aria-label="X" />
            <UButton
                icon="i-simple-icons-github"
                color="neutral"
                variant="ghost"
                to="https://github.com/nuxt/nuxt"
                target="_blank"
                aria-label="GitHub" />
        </template> -->
    </UFooter>
</template>
