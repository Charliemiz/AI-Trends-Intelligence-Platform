<template>
  <div class="min-h-screen p-4">
    <h2 class="text-xl font-bold mb-4">Articles</h2>
    <div class="flex justify-end p-4">
      <span class="pr-4">Search Articles: </span>
      <input class="bg-white text-black rounded-lg" v-model="searchQuery" @change="OnSearchChange" ></input>
    </div>
    <div class="w-full overflow-x-auto">
      <table class="border-collapse border border-gray-400 w-full">
        <thead>
          <tr class="bg-gray-100 text-black">
            <th class="border border-gray-400 px-4 py-2 text-left">Title</th>
            <th class="border border-gray-400 px-4 py-2 w-60">Created On</th>
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
                <span>
                    {{ new Date(a.created_at).toLocaleString() }}
                </span>
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
const searchQuery = ref('')

onMounted(async () => {
  const data = await fetchArticles()
  articles.value = data
})

async function fetchArticles() {
  try {
    const response = await apiRequest('/api/articles', { method: 'GET' })
    console.log('Fetched articles:', response)
    return response
  } catch (e) {
    console.error('Failed to fetch articles:', e.message)
    return []
  }
}

async function OnSearchChange() {
    try {
        const response = await apiRequest(`/api/articles?search=${searchQuery.value}`, { method: 'GET' })
        console.log('Fetched articles:', response)
        articles.value = response
    } catch (e) {
        console.error('Failed to fetch articles:', e.message)
        articles.value = []
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