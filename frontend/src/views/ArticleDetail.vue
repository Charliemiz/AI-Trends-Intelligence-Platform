<template>
    <div>
        <div>
            <h1 class="article-title text-4xl md:text-5xl font-extrabold text-blue-600">{{ article.title }}</h1>
            <div class="article-content mt-8" v-html="renderedContent"></div>
            <br/>
            <h2 class="text-2xl font-semibold text-blue-600 mt-8 mb-4">Sources:</h2>
            <div v-for="s in article.sources" :key="s.id">
                <a :href="s.url" target="_blank" class="text-blue-600 underline">
                    {{ s.title }}
                </a>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { apiRequest } from '@/utils/api'

const route = useRoute()

const article = ref({ title: '', content: '', sources: [] })

onMounted(async () => {
    const data = await fetchArticleById(route.params.id)
    article.value = data || { title: '', content: '', sources: [] }
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

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\"/g, '&quot;')
        .replace(/'/g, '&#39;')
}

const renderedContent = computed(() => {
    const text = article.value?.content || ''
    if (!text) return ''

    const lines = text.split(/\r?\n/)
    const out = []
    let paragraphBuffer = []

    const flushParagraph = () => {
        if (paragraphBuffer.length) {
            out.push(`<p class="mb-3 text-base leading-7">${paragraphBuffer.join(' ')}</p>`)
            paragraphBuffer = []
        }
    }

    for (let rawLine of lines) {
        const line = rawLine.trim()
        if (line === '') {
            flushParagraph()
            continue
        }

        const headerMatch = line.match(/^\*\*(.+?)\*\*$/)
        if (headerMatch) {
            flushParagraph()
            out.push(`<h2 class="text-2xl font-semibold text-blue-600 mt-8 mb-4">${escapeHtml(headerMatch[1])}</h2>`)
        } else {
            paragraphBuffer.push(escapeHtml(line))
        }
    }

    flushParagraph()
    return out.join('\n')
})

</script>