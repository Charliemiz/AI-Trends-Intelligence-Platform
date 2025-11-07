<template>
  <div class="min-h-screen p-4">
    <h2 class="text-xl font-bold mb-4">Articles</h2>
    <div class="w-full overflow-x-auto">
      <table class="border-collapse border border-gray-400 w-full">
        <thead>
          <tr class="bg-gray-100 text-black">
            <th class="border border-gray-400 px-4 py-2 text-left">Title</th>
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
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiRequest } from '@/utils/api'
const articles = ref([])

onMounted(async () => {
  const data = await fetchArticles()
  articles.value = data
})

async function fetchArticles() {
  try {
    const response = await apiRequest('/articles', { method: 'GET' })
    console.log('Fetched articles:', response)
    return response
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