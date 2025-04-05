export default defineNuxtPlugin((nuxtApp) => {
    nuxtApp.hook("page:finish", () => {
        // Check if we're on specific routes
        const route = useRoute();
        if (route.path.startsWith("/collection/page")) {
            window.scrollTo({
                top: 0,
                behavior: "smooth",
            });
        }
    });
});
