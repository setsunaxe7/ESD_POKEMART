<script setup lang="ts">
    import type { NavigationMenuItem } from "@nuxt/ui";
    const route = useRoute();

    const items = ref<NavigationMenuItem[]>([
        {
            label: "Collection",
            to: "/collection/page/1",
            active: computed(() => route.path.startsWith("/collection")),
        },
        {
            label: "Marketplace",
            to: "/marketplace",
            active: computed(() => route.path.startsWith("/marketplace")),
        },
        {
            label: "Sell Cards",
            to: "/sell",
            active: computed(() => route.path.startsWith("/sell")),
        },
        {
            label: "Grade Cards",
            to: "/grading",
            active: computed(() => route.path.startsWith("/grading")),
        },
        {
            label: "Refund",
            to: "/refund",
            active: computed(() => route.path.startsWith("/refund")),
        },
    ]);

    const user = useSupabaseUser();
</script>

<template>
    <UHeader>
        <template #title>
            <div class="flex items-center gap-2">
                <img src="../assets/img/logo.png" alt="logo" class="h-8 w-auto logo-image" />
                <h1 class="text-xl font-bold brand-name">Bulba-Trade</h1>
            </div>
        </template>

        <UNavigationMenu class="w-full justify-center" :items="items" />

        <template #right>
            <UColorModeButton />

            <template v-if="user">
                <UButton to="/account">My Account</UButton>
                <UButton to="/logout">Logout</UButton>
            </template>
            <template v-else>
                <UButton to="/login">Login</UButton>
            </template>

            <!-- <UTooltip text="Open on GitHub" :kbds="['meta', 'G']">
                <UButton
                    color="neutral"
                    variant="ghost"
                    to="https://github.com/setsunaxe7/ESD_POKEMART"
                    target="_blank"
                    icon="i-simple-icons-github"
                    aria-label="GitHub" />
            </UTooltip> -->
        </template>
    </UHeader>
</template>

<style>
    .brand-name {
        background: linear-gradient(
            to left,
            oklch(0.723 0.219 149.579),
            oklch(0.69 0.215 149),
            oklch(0.66 0.21 148.5),
            oklch(0.63 0.205 148),
            oklch(0.6 0.2 147.5)
        );
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-family: var(--font-open-sans);
        font-weight: 800;
    }

    .logo-image {
        filter: brightness(1.3);
    }
</style>
