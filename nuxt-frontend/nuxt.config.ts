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
    supabase: {
        redirectOptions: {
            login: '/login',
            callback: '/confirm',
            include: undefined,
            exclude: ['/', '/signup', '/marketplace', '/collection', '/grading', '/listings/**'],
            saveRedirectToCookie: true,
        }
    }
});