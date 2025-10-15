import { ref } from 'vue';

export function useNeonAPI() {
    const loading = ref(false);
    const error = ref(null);

    const API_ENDPOINT = 'https://ep-long-fog-a8xj8s2o.apirest.eastus2.azure.neon.tech/neondb/rest/v1';

    const fetchTable = async (tableName) => {
        loading.value = true;
        error.value = null;

        try {
            const response = await fetch(`${API_ENDPOINT}/${tableName}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (err) {
            error.value = err.message;
            console.error('Neon API Error:', err);
            throw err;
        } finally {
            loading.value = false;
        }
    };

    return {
        loading,
        error,
        fetchTable
    };
}