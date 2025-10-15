import { ref } from 'vue';

export function useArticles() {
    const loading = ref(false);
    const error = ref(null);
    const articles = ref([]);

    const fetchArticles = async () => {
        loading.value = true;
        error.value = null;

        try {
            // Call your Vercel serverless function
            const response = await fetch('/api/articles');

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            articles.value = await response.json();
            console.log('Articles fetched:', articles.value);
            return articles.value;
        } catch (err) {
            error.value = err.message;
            console.error('Failed to fetch articles:', err);
            return [];
        } finally {
            loading.value = false;
        }
    };

    return {
        articles,
        loading,
        error,
        fetchArticles
    };
}