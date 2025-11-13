<template>
    <div>
        <h1>Article Detail</h1>
        <p>Article ID: {{ route.params.id }}</p>
        <br />
    </div>
    <div>
        <span class="flex pb-4 text-3xl font-semibold text-blue-500">{{ article.title }}</span>
        {{ article.content }}        
        <span class="flex text-3xl font-semibold text-blue-500 py-4">Sources:</span>
        <div v-for="s in article.sources" :key="s.id">
            <a :href="s.url" target="_blank" class="text-blue-500 underline">
                {{ s.title }}
            </a>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiRequest } from '@/utils/api'

const route = useRoute()

const article = ref([])

onMounted(async () => {
    const data = await fetchArticleById(route.params.id)
    article.value = data
})

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

</script>