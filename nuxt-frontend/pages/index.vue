<script setup lang="ts">
    const links = ref([
        {
            label: "Shop Cards",
            to: "/marketplace",
            size: "xl",
            icon: "i-material-symbols:shopping-bag-outline",
        },
        {
            label: "Grade Cards",
            to: "/grading",
            color: "neutral",
            size: "xl",
            variant: "subtle",
            trailingIcon: "i-material-symbols:frame-inspect-rounded",
        },
    ]);

    const cards = ref([
        {
            title: "Explore Cards",
            description:
                "Browse the complete Scarlet & Violet 151 collection with detailed card information.",
            to: "/collection",
        },
        {
            title: "Grade Cards",
            description:
                "Send your valuable cards for professional grading and authentication services.",
            to: "/grading",
        },
        {
            title: "Sell Cards",
            description:
                "List your cards for sale or auction and reach thousands of collectors worldwide.",
            to: "/marketplace",
        },
    ]);

    const icons = ref([
        "i-material-symbols:search",
        "i-material-symbols:award-star-outline-rounded",
        "i-material-symbols:attach-money-rounded",
    ]);

    const features = ref([
        {
            title: "Authenthication Guarantee",
            description: "Every card is thoroughly examined for authenticity by certified experts.",
            icon: "i-material-symbols:shield-spark-rounded",
        },
        {
            title: "Meticulous Assessment",
            description:
                "Cards are evaluated based on centering, corners, edges, and surface quality.",
            icon: "i-material-symbols:rewarded-ads",
        },
        {
            title: "Increased Value",
            description:
                "Graded cards typically sell for significantly more than their ungraded counterparts.",
            icon: "i-material-symbols:trending-up",
        },
    ]);
    const gradingLink = ref([
        {
            label: "Start Grading",
            to: "grading",
            color: "primary",
            variant: "solid",
            size: "xl",
            trailingIcon: "i-lucide-arrow-right",
        },
    ]);
</script>

<template>
    <UContainer>
        <UPageHero
            title="Discover the Scarlet & Violet 151 Collection"
            description="The premier marketplace for Pokémon TCG enthusiasts. Buy, sell, and grade your cards with confidence."
            orientation="horizontal"
            :links="links">
            <img
                src="../assets//img/index/151.png"
                alt="App screenshot"
                class="rounded-lg shadow-2xl ring ring-(--ui-border)" />
        </UPageHero>
        <UPageSection
            title="Professional Card Grading"
            description="Unlock the full value of your collection with our expert grading service. We partner with industry-leading graders to authenticate and evaluate your cards."
            orientation="horizontal"
            :features="features"
            :links="gradingLink"
            reverse>
            <img
                src="../assets/img/index/grading.png"
                alt="Illustration"
                class="w-full rounded-[calc(var(--ui-radius)*2)] scale-110" />
        </UPageSection>
        <UPageGrid>
            <UPageCard
                v-for="(card, index) in cards"
                :key="index"
                v-bind="card"
                spotlight
                spotlight-color="primary"
                class="text-center">
                <template #header>
                    <div class="mb-4 flex justify-center">
                        <div class="rounded-full p-3 inline-flex items-center justify-center">
                            <UIcon :name="icons[index]" class="size-12" />
                        </div>
                    </div>
                </template>
            </UPageCard>
        </UPageGrid>
    </UContainer>
</template>

<style>
    section [class^="iconify i-material-symbols\:"] {
        width: 2rem;
        height: 2rem;
        margin-right: 1rem;
    }
</style>
