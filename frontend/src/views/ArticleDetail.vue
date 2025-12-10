<template>
    <div class="fixed inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white overflow-y-auto">
        <div class="max-w-6xl mx-auto px-8 py-8">
            <!-- Back Button -->
            <router-link to="/articles"
                class="inline-flex items-center gap-2 text-yellow-400 hover:text-yellow-300 mb-8 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                </svg>
                Back to Articles
            </router-link>

            <!-- Article Title -->
            <h1
                class="text-5xl md:text-6xl font-extrabold mb-8 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                {{ article.title }}
            </h1>

            <!-- Meta Information -->
            <div class="flex flex-wrap items-center gap-4 mb-8 pb-6 border-b border-slate-700">
                <span v-if="article.created_at" class="flex items-center gap-2 text-slate-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z">
                        </path>
                    </svg>
                    {{ formatDate(article.created_at) }}
                </span>
                <!-- Impact + Sector -->
                <div class="flex items-center gap-4">
                    <span v-if="article.impact_score && article.impact_score > 0" class="px-3 py-1 rounded-full text-sm font-semibold 
                    bg-yellow-900 border border-yellow-600 text-yellow-300">
                        Impact: {{ article.impact_score }}
                    </span>

                    <span v-if="article.sector" class="px-3 py-1 rounded-full text-sm font-semibold 
                    bg-emerald-900 border border-emerald-600 text-emerald-300">
                        {{ article.sector }}
                    </span>
                </div>
            </div>

            <!-- Tags -->
            <div v-if="article.tags && article.tags.length > 0" class="mb-8">
                <div class="flex flex-wrap gap-2">
                    <span v-for="tag in article.tags" :key="tag.id"
                        class="px-4 py-2 bg-blue-900 border border-blue-600 text-blue-300 rounded-lg text-sm font-semibold hover:bg-blue-800 transition-colors">
                        {{ tag.name }}
                    </span>
                </div>
            </div>

            <!-- Article Content -->
            <div class="prose prose-invert max-w-none mb-12">
                <div class="text-slate-200 leading-relaxed text-lg article-content" v-html="renderedContent"></div>
            </div>

            <!-- Sources Section -->
            <div v-if="article.sources && article.sources.length > 0" class="mt-12 pt-8 border-t border-slate-700">
                <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
                    <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.658 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1">
                        </path>
                    </svg>
                    Sources
                </h2>
                <div class="grid gap-3">
                    <a v-for="(source, index) in article.sources" :key="source.id" :href="source.url" target="_blank"
                        class="group p-4 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 hover:border-blue-500 transition-all">
                        <div class="flex items-start gap-3">
                            <svg class="w-5 h-5 text-blue-400 mt-1 flex-shrink-0" fill="none" stroke="currentColor"
                                viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14">
                                </path>
                            </svg>
                            <div class="flex justify-between w-full items-center">
                                <div class="flex-col">
                                    <h3 class="font-semibold text-blue-400 group-hover:text-blue-300 transition-colors">
                                        {{ source.title }}
                                    </h3>
                                    <p class="text-slate-400 text-sm mt-1">{{ source.domain || source.url }}</p>
                                </div>
                                <div class="font-semibold text-xl justify-center items-center">[{{ index + 1 }}]</div>
                            </div>
                        </div>
                    </a>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
/**
 * ArticleDetail View Component
 * 
 * Displays a single article with full content, metadata, and sources.
 * Renders markdown content as HTML and provides navigation back to the list.
 * This view serves as the container for the ChatWidget component.
 * 
 * Features:
 * - Fetches and displays full article details by ID
 * - Renders markdown content with custom heading styles
 * - Displays article metadata (title, date, impact score, tags)
 * - Shows clickable source links with external link indicators
 * - Back navigation to article list
 * - Provides context for the ChatWidget component
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiRequest } from '@/utils/api'
import { marked } from 'marked';

const route = useRoute()

/** Article data object containing all article information */
const article = ref({ title: '', content: '', sources: [], tags: [], created_at: null, impact_score: -1 })

/**
 * Custom markdown renderer for styled headers
 * Configures heading elements with consistent font weight and sizing
 */
const renderer = new marked.Renderer();
renderer.heading = ({ text, depth }) => {
    return `<h${depth} style="font-weight: 700; margin-top: 1rem; font-size: 2rem;">${text}</h${depth}>`;
};

/**
 * Configure marked library options for GitHub-flavored markdown
 * Enables line breaks, header IDs, and custom rendering
 */
marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: true,
    mangle: false,
    renderer: renderer
})

/**
 * Computed property that converts markdown content to HTML
 * 
 * @returns {string} HTML-rendered article content
 */
const renderedContent = computed(() => {
    if (!article.value.content) return ''
    return marked(article.value.content)
})

/**
 * Fetch article data when component mounts
 * Extracts article ID from route params
 */
onMounted(async () => {
    const data = await fetchArticleById(route.params.id)
    article.value = data || { title: '', content: '', sources: [], tags: [], created_at: null, impact_score: -1 }
})

/**
 * Fetch a single article by ID from the API
 * 
 * @param {string|number} id - The article ID from the route
 * @returns {Promise<Object>} Article object with all metadata
 */
async function fetchArticleById(id) {
    try {
        const res = await apiRequest(`/api/articles/${id}`, { method: 'GET' })
        console.log('Fetched article:', res)
        return res
    } catch (e) {
        console.error('Failed to fetch article:', e.message)
        return {}
    }
}

/**
 * Format a date string for display with time
 * 
 * @param {string} dateString - ISO date string from the API
 * @returns {string} Formatted date like "January 15, 2024 at 10:30 AM"
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }
    return new Date(dateString).toLocaleDateString('en-US', options)
}
</script>