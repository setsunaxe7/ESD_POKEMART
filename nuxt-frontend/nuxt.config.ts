import tailwindcss from "@tailwindcss/vite";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: "2024-11-01",
    devtools: { enabled: true },
    modules: ["@nuxt/ui-pro", "@nuxtjs/supabase"],
    css: ["~/assets/styles/main.css", "animate.css/animate.min.css"],
    vite: {
        plugins: [tailwindcss()],
    },
    services: [{ src: "~/services/websocketService.js", mode: "client" }],
    supabase: {
        redirectOptions: {
            login: '/login',
            callback: '/confirm',
            include: ['/grading'],
            exclude: ['/', '/signup', '/marketplace', '/collection', '/listing/**',],
            saveRedirectToCookie: true,
        }
    }
});