<script setup lang="ts">
    import { USelectMenu } from "#components";

    const refundReason = ["Card Damaged", "Item not as described", "Others"];
</script>

<template>
    <UMain class="min-h-[calc(100vh-var(--header-height)-var(--footer-height))]">
        <UContainer>
            <UPageSection
                title="Refund Request"
                description="Submit a refund request for an unstatifactory order"
                :ui="{ container: 'lg:py-24' }" />
            <UCard class="p-4 mb-8">
                <div class="space-y-8">
                    <div class="space-y-2">
                        <h1 class="text-2xl font-bold">Request form</h1>
                        <p class="text-gray-500">
                            Fill up this form accordingly to submit a refund request for review
                        </p>
                    </div>
                    <div class="grid grid-cols-3 gap-12">
                        <div class="col-span-2 flex flex-col space-y-6">
                            <div class="space-y-2">
                                <p class="font-medium">Choose an order</p>
                                <USelectMenu
                                    class="w-3/4"
                                    placeholder="Select transaction"></USelectMenu>
                            </div>
                            <div class="space-y-2">
                                <p class="font-medium">Reason for request</p>
                                <USelectMenu
                                    class="w-3/4"
                                    :items="refundReason"
                                    placeholder="Select reason"></USelectMenu>
                            </div>
                            <div class="space-y-2">
                                <p class="font-medium">Elaboration for reason</p>
                                <UTextarea
                                    class="w-3/4"
                                    placeholder="Provide a detailed explanation for the reason of this refund request"
                                    :rows="4"></UTextarea>
                            </div>
                        </div>
                    </div>
                </div>
            </UCard>
            <div class="w-full flex">
                <UButton size="xl" :block="true" class="w-1/2 m-auto">Submit Request</UButton>
            </div>
        </UContainer>
    </UMain>
</template>
