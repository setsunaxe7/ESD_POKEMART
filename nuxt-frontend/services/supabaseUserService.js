class SupabaseUserService {
    constructor(supabaseClient) {
        this.client = supabaseClient;
    }

    // Fetch user data
    async fetchUserData(user) {
        try {
            if (!user) {
                return;
            }

            // Get user data from Supabase
            const { data, error } = await this.client.auth.getUser();

            if (error) {
                throw error;
            }

            if (data && data.user) {
                console.log('User data from Supabase:', data.user);

                // Return the entire user object
                return data.user;  
            }
        } catch (error) {
            console.error('Error fetching user data:', error);
            throw error;
        }
    }
}

export default SupabaseUserService;
