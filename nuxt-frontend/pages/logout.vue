<script setup lang="ts">
const supabase = useSupabaseClient()
const user = useSupabaseUser()

await supabase.auth.signOut();

watch(user, () => {
  if (!user.value) { navigateTo('/') }
}, { immediate: true })
</script>

<template>
    <UMain>
        <UContainer>
            <p>Signing out...</p>
        </UContainer>
    </UMain>
</template>