<template>
  <div class="about p-8 space-y-6">
    <h1 class="text-3xl font-bold">About Page</h1>

    <div class="flex flex-col space-y-4 max-w-md">
      <input
        v-model="url"
        type="text"
        placeholder="Enter URL"
        class="border p-2 rounded"
      />
      <textarea
        v-model="summary"
        placeholder="Enter summary text"
        class="border p-2 rounded"
      ></textarea>

      <button @click="saveSummary" class="bg-blue-500 text-white px-4 py-2 rounded">
        Add Summary
      </button>

      <button @click="searchPerplexity" class="bg-green-500 text-white px-4 py-2 rounded">
        Search Perplexity
      </button>

      <div v-if="loading" class="text-gray-500">Loading...</div>

      <pre v-if="result" class="bg-gray-100 text-black p-4 rounded overflow-x-auto">{{ result }}</pre>
      <p v-if="error" class="text-red-500 font-semibold">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const url = ref('')
const summary = ref('')
const result = ref('')
const error = ref('')
const loading = ref(false)

async function req(path, init) {
  const res = await fetch(`http://localhost:8000${path}`, {
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

async function saveSummary() {
  error.value = ''
  result.value = ''
  loading.value = true
  try {
    const res = await req(
      `/summary/add?url=${encodeURIComponent(url.value)}&summary=${encodeURIComponent(summary.value)}`,
      { method: 'POST' }
    )
    result.value = res
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function searchPerplexity() {
  error.value = ''
  result.value = ''
  loading.value = true
  try {
    const res = await req(
      `/perplexity/search?query=How is the stock market doing today?`,
      { method: 'POST' }
    )
    result.value = res
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
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
