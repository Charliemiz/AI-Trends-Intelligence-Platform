<template>
  <div class="fixed inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white overflow-y-auto">
    <!-- Header -->
    <div class="max-w-6xl mx-auto px-8 py-8">
      <h1
        class="text-5xl md:text-6xl font-extrabold mb-2 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
        AI Trends
      </h1>
      <p class="text-slate-400 text-lg mb-8">Stay informed with the latest AI insights</p>

      <!-- Search Bar -->
      <div class="mb-12">
        <div class="relative flex items-center">
          <svg class="absolute left-4 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
          <input v-model="searchQuery" @input="OnSearchChange" type="text" placeholder="Search Articles..."
            class="w-full pl-12 pr-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition" />
        </div>
      </div>

      <!-- Articles Grid -->
      <div v-if="articles.length > 0" class="space-y-4">
        <router-link v-for="article in articles" :key="article.id" :to="`/articles/${article.id}`"
          class="group cursor-pointer p-6 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 hover:border-blue-500 transition-all duration-300 transform hover:scale-105 relative block">
          <!-- Title + Sector -->
          <div class="flex items-center gap-3 mb-2">
            <h3 class="text-2xl font-bold text-white group-hover:text-blue-400 transition-colors">
              {{ article.title }}
            </h3>

            <span v-if="article.sector" class="shrink-0 px-2.5 py-0.5 text-xs font-semibold rounded-full 
            bg-emerald-900 border border-emerald-600 text-emerald-300">
              {{ article.sector }}
            </span>
          </div>

          <!-- Tags (if available) -->
          <div v-if="article.tags && article.tags.length > 0" class="flex flex-wrap gap-2 mb-4">
            <span v-for="tag in article.tags" :key="tag.id"
              class="px-3 py-1 bg-blue-900 border border-blue-600 text-blue-300 rounded-full text-xs font-semibold">
              {{ tag.name }}
            </span>
          </div>

          <!-- Created Date and Impact Score -->
          <div class="flex items-center justify-between">
            <p class="text-slate-400 text-sm">
              📅 {{ formatDate(article.created_at) }}
            </p>
            <div v-if="article.impact_score !== null" class="text-right">
              <p class="text-xs text-slate-500 mb-1">Impact</p>
              <p class="text-lg font-bold text-yellow-400">{{ article.impact_score }}</p>
            </div>
          </div>
        </router-link>
      </div>

      <!-- Pagination Controls -->
      <div v-if="totalPages > 1" class="mt-12 flex items-center justify-center gap-4">
        <button @click="prevPage" :disabled="currentPage === 1"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition">
          ← Previous
        </button>

        <div class="flex items-center gap-2">
          <span class="text-slate-400">Page</span>
          <input v-model.number="currentPage" @input="goToPage" type="text" inputmode="numeric" :max="totalPages"
            min="1"
            class="w-16 px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-center focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <span class="text-slate-400">of {{ totalPages }}</span>
        </div>

        <button @click="nextPage" :disabled="currentPage === totalPages"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition">
          Next →
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="articles.length === 0" class="text-center py-16">
        <svg class="mx-auto w-16 h-16 text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v4m0 0a2 2 0 012 2v4a2 2 0 01-2 2m0 0H9m0 0a2 2 0 01-2-2V6a2 2 0 012-2m0 0H9">
          </path>
        </svg>
        <p class="text-slate-400 text-lg">No articles found</p>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * ArticleList View Component
 * 
 * Displays a paginated, searchable list of AI trend articles.
 * Shows article titles, tags, creation dates, and impact scores.
 * Supports real-time search filtering and page navigation.
 * 
 * Features:
 * - Paginated article listing with configurable page size
 * - Real-time search filtering by article title
 * - Interactive pagination controls (prev/next/direct page input)
 * - Displays article metadata (tags, date, impact score)
 * - Empty state when no articles match search criteria
 * - Smooth scroll to top on page change
 */
import { ref, onMounted } from 'vue'
import { apiRequest } from '@/utils/api'

/** Array of article objects to display */
const articles = ref([])

/** Current search query string */
const searchQuery = ref('')

/** Current page number (1-indexed) */
const currentPage = ref(1)

/** Number of articles to display per page */
const pageSize = ref(20)

/** Total number of pages available */
const totalPages = ref(0)

/** Total count of articles matching current filters */
const totalCount = ref(0)

/**
 * Fetch articles on component mount
 */
onMounted(async () => {
  await fetchArticles()
})

/**
 * Fetch articles from the API with current pagination and search parameters
 * 
 * Constructs query parameters from current state (page, page_size, search)
 * and updates the articles list along with pagination metadata. Scrolls
 * the container to top after fetching.
 */
async function fetchArticles() {
  try {
    const query = new URLSearchParams({
      page: currentPage.value,
      page_size: pageSize.value,
      ...(searchQuery.value && { search: searchQuery.value })
    }).toString()

    const response = await apiRequest(`/api/articles?${query}`, { method: 'GET' })
    console.log('Fetched articles response:', response)

    articles.value = response.items || []
    totalCount.value = response.total_count || 0
    totalPages.value = response.total_pages || 0
    currentPage.value = response.page || 1

    // Scroll to top of the scrollable container smoothly
    const container = document.querySelector('.fixed.inset-0.overflow-y-auto')
    if (container) {
      container.scrollTo({ top: 0, behavior: 'smooth' })
    }
  } catch (e) {
    console.error('Failed to fetch articles:', e.message)
    articles.value = []
    totalPages.value = 0
    totalCount.value = 0
  }
}

/**
 * Handle search input changes
 * 
 * Resets to page 1 when user types in the search box to ensure
 * they see results from the beginning of the filtered list.
 */
async function OnSearchChange() {
  // Reset to page 1 when searching
  currentPage.value = 1
  await fetchArticles()
}

/**
 * Navigate to the next page
 * 
 * Increments the page number and fetches articles if not already
 * on the last page.
 */
function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value += 1
    fetchArticles()
  }
}

/**
 * Navigate to the previous page
 * 
 * Decrements the page number and fetches articles if not already
 * on the first page.
 */
function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value -= 1
    fetchArticles()
  }
}

/**
 * Navigate to a specific page number
 * 
 * Validates the user-entered page number and fetches articles.
 * If invalid, clamps the value to the valid range [1, totalPages].
 */
async function goToPage() {
  if (currentPage.value >= 1 && currentPage.value <= totalPages.value) {
    await fetchArticles()
  } else {
    // Reset to valid page if user enters invalid number
    currentPage.value = Math.max(1, Math.min(currentPage.value, totalPages.value))
  }
}

/**
 * Format a date string for display
 * 
 * @param {string} dateString - ISO date string from the API
 * @returns {string} Formatted date like "Jan 15, 2024"
 */
function formatDate(dateString) {
  const options = { year: 'numeric', month: 'short', day: 'numeric' }
  return new Date(dateString).toLocaleDateString('en-US', options)
}
</script>