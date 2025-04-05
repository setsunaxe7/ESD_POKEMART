<script setup lang="ts">
import * as v from 'valibot'

const isButtonPressed = ref(false)
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

// Handle button click animation
const handleButtonClick = () => {
  isButtonPressed.value = true
}
</script>

<template>
  <UMain>
    <UContainer class="max-w-md mx-auto py-10">
      <h1 class="text-2xl font-bold mb-6">Login</h1>
      <UForm :schema="schema" :state="state" class="space-y-4" @submit="sign_in">
          <UFormField label="Email" name="email">
            <UInput v-model="state.email" placeholder="you@email.com" class="w-full max-w"/>
          </UFormField>

          <UButton type="submit" @click="handleButtonClick" class="w-full max-w justify-center">
          Submit
          </UButton>
      </UForm>
      <div v-if="isButtonPressed">
        Magic Link sent to your email. Click on the link in the email to log in!
      </div>
    </UContainer>
  </UMain>
</template>