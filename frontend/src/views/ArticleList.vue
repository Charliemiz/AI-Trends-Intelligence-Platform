<template>
  <div class="min-h-screen p-4">
    <h2 class="text-xl font-bold mb-4">Articles</h2>
    <div class="w-full overflow-x-auto">
      <table class="border-collapse border border-gray-400 w-full">
        <thead>
          <tr class="bg-gray-100 text-black">
            <th class="border border-gray-400 px-4 py-2 text-left">Title</th>
            <th class="border border-gray-400 px-4 py-2 text-left">Sources</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in articles" :key="a.id">
            <td class="border border-gray-400 px-4 py-2">
              <router-link :to="`/articles/${a.id}`">
                <span class="text-blue-500 underline cursor-pointer">
                  {{ a.title }}
                </span>
              </router-link>
            </td>
            <td class="border border-gray-400 px-4 py-2">
              <div v-for="s in a.sources" :key="s.id">
                <a :href="s.url" target="_blank" class="text-blue-500 underline">
                  {{ s.name }}
                </a>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
// const url = ref('')
// const summary = ref('')
// const result = ref('')
// const error = ref('')
// const loading = ref(false)
const articles = ref([])
const BASE = import.meta.env.VITE_API_BASE_URL

onMounted(async () => {
  const data = await fetchArticles()
  articles.value = data
})

async function req(path, init) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    ...init,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`HTTP ${res.status}: ${text}`)
  }
  const ct = res.headers.get('content-type') || ''
  return ct.includes('application/json') ? res.json() : res.text()
}

// async function saveSummary() {
//   error.value = ''
//   result.value = ''
//   loading.value = true
//   try {
//     const res = await req(
//       `/summary/add?url=${encodeURIComponent(url.value)}&summary=${encodeURIComponent(summary.value)}`,
//       { method: 'POST' }
//     )
//     result.value = res
//   } catch (e) {
//     error.value = e.message
//   } finally {
//     loading.value = false
//   }
// }

// async function searchPerplexity() {
//   error.value = ''
//   result.value = ''
//   loading.value = true
//   try {
//     const res = await req(
//       `/perplexity/search?query=How is the stock market doing today?`,
//       { method: 'GET' }
//     )
//     result.value = res
//   } catch (e) {
//     error.value = e.message
//   } finally {
//     loading.value = false
//   }
// }

async function fetchArticles() {
  try {
    const res = await req('/articles', { method: 'GET' })
    console.log('Fetched articles:', res)
    return res
  } catch (e) {
    console.error('Failed to fetch articles:', e.message)
    return []
  }
}

</script>

<style scoped>
.about {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
</style>