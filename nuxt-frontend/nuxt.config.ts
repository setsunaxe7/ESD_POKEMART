import tailwindcss from "@tailwindcss/vite";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: "2024-11-01",
    devtools: { enabled: true },
    modules: ["@nuxt/ui-pro"],
    css: ["~/assets/styles/main.css", "animate.css/animate.min.css"],
    vite: {
        plugins: [tailwindcss()],
    },
});
