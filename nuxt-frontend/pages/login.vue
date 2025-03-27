<script setup lang="ts">
import * as v from 'valibot'
import type { FormSubmitEvent } from '@nuxt/ui'

const schema = v.object({
    email: v.pipe(v.string(), v.email('Invalid email')),
})

type Schema = v.InferOutput<typeof schema>

const state = reactive({
  email: '',
  password: ''
})

const supabase = useSupabaseClient()

async function sign_in() {
  const { error } = await supabase.auth.signInWithOtp({
    email: state.email,
    options: {
      emailRedirectTo: 'http://localhost:3000/confirm',
    }
  })
  if (error) console.log(error)
}
</script>
<template>
    <UMain>
        <UContainer>
            <h1>login</h1>
            <UForm :schema="schema" :state="state" class="space-y-4" @submit="sign_in">
                <UFormField label="Email" name="email">
                <UInput v-model="state.email" />
                </UFormField>

                <UButton type="submit">
                Submit
                </UButton>
            </UForm>
        </UContainer>
    </UMain>
</template>