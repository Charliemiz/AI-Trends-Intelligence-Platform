<template>
    <div class="max-w-4xl mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold text-white mb-8">Articles</h1>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-10">
            <p class="text-gray-400 text-lg">Loading articles...</p>
        </div>

        <!-- Error State -->
        <div v-if="error" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-lg mb-6">
            <p class="font-medium">Error: {{ error }}</p>
        </div>

        <!-- No Articles State -->
        <div v-if="!loading && articles.length === 0" class="text-center py-10">
            <p class="text-gray-500">No articles found.</p>
        </div>

        <!-- Articles List -->
        <div class="space-y-6">
            <div v-for="article in articles" :key="article.id"
                class="bg-white border border-gray-200 rounded-lg p-6 transition-shadow duration-200 hover:shadow-lg">
                <h3 class="text-xl font-semibold text-gray-900 mb-3">
                    {{ article.title }}
                </h3>

                <a :href="article.url" target="_blank"
                    class="inline-block text-blue-600 font-semibold hover:underline mb-3">
                    Read more →
                </a>

                <p class="text-gray-600 text-sm mb-3">
                    Source: {{ article.source }}
                </p>

                <p class="text-gray-700 text-sm leading-relaxed">
                    {{ article.summary }}
                </p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useArticles } from '@/../composables/useArticles';

const { articles, loading, error, fetchArticles } = useArticles();

onMounted(() => {
    fetchArticles();
});
</script>