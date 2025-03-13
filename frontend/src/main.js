import { createApp, h } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'
import App from './App.vue'
import about from './views/about.vue'
import home from './views/home.vue'
import login from './views/login.vue'
import market from './views/market.vue'

import HelloWorld from './components/HelloWorld.vue'

const routes = [
  { path: '/', component: HelloWorld },
  { path: '/about', component: about },
  { path: '/home', component: home },
  { path: '/login', component: login },
  { path: '/market', component: market }
]

const router = createRouter({
    history: createWebHistory(),
    routes: routes
})

createApp(App)
    .use(router)
    .mount('#app')
