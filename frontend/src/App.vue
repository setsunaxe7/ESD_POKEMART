<script setup>
import HelloWorld from './components/HelloWorld.vue'

import { createMemoryHistory, createRouter } from 'vue-router'

import Market from './components/Market.vue'

const routes = [
  { path: '/', component: HelloWorld },
  { path: '/about', component: Market },
]

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})
</script>

<template>
  <div>
    <a href="https://vite.dev" target="_blank">
      <img src="/vite.svg" class="logo" alt="Vite logo" />
    </a>
    <a href="https://vuejs.org/" target="_blank">
      <img src="./assets/vue.svg" class="logo vue" alt="Vue logo" />
    </a>
    <h1> Bulba-Trade | 卡片皇朝 </h1>
    <div class="enterprise-details" style="margin-top: 20px">
      Already have an account?<router-link to="/about">LOGIN</router-link>
    </div>
  </div>
  <HelloWorld msg="" />
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
