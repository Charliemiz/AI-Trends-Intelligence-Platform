<template>
  <!-- Only show chat widget on article detail pages -->
  <div v-if="isArticleDetail" class="fixed bottom-6 right-6 w-80">
    <!-- Collapsed Chat Button -->
    <button
      v-if="!isOpen && sessionId"
      @click="isOpen = true"
      class="bg-blue-600 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg hover:bg-blue-700 transition"
    >
      💬
    </button>

    <!-- Loading button while creating session -->
    <button
      v-else-if="!isOpen && sessionCreating"
      disabled
      class="bg-gray-400 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg cursor-not-allowed"
    >
      ⏳
    </button>

    <!-- Chat Box -->
    <div
      v-else-if="isOpen && sessionId"
      class="bg-white shadow-xl rounded-2xl flex flex-col overflow-hidden border border-gray-200"
    >
      <div class="bg-blue-600 text-white p-3 flex justify-between items-center">
        <h3 class="font-semibold">Ask the Analyst</h3>
        <button @click="isOpen = false" class="text-white hover:text-gray-300">✕</button>
      </div>

      <div class="flex-1 p-3 overflow-y-auto h-64 space-y-2">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="msg.role === 'user' ? 'text-right' : 'text-left'"
        >
          <div
            :class="[
              'inline-block px-3 py-2 rounded-lg',
              msg.role === 'user'
                ? 'bg-blue-100 text-blue-800'
                : 'bg-gray-100 text-gray-800'
            ]"
          >
            {{ msg.content }}
          </div>
        </div>
      </div>

      <form @submit.prevent="sendMessage" class="p-3 border-t flex">
        <input
          v-model="input"
          type="text"
          placeholder="Ask a question..."
          :disabled="isLoading"
          class="flex-1 border rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring focus:ring-blue-300 disabled:bg-gray-100"
        />
        <button
          type="submit"
          :disabled="isLoading || !input.trim()"
          class="ml-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
        >
          {{ isLoading ? "..." : "Send" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from "vue";
import { useRoute } from "vue-router";
import { apiRequest } from "@/utils/api";

const route = useRoute();
const isOpen = ref(false);
const input = ref("");
const messages = ref([]);
const sessionId = ref(null);
const isLoading = ref(false);
const sessionCreating = ref(false);

// Check if we're on an article detail page
const isArticleDetail = computed(() => {
  // More reliable check - just check if URL matches pattern
  const matches = route.path.match(/^\/articles\/\d+$/);
  return !!matches;
});

// Extract article ID from route
const articleId = computed(() => {
  const match = route.path.match(/^\/articles\/(\d+)$/);
  return match ? parseInt(match[1], 10) : null;
});

// Watch for route changes and create/close sessions
watch([isArticleDetail, articleId], async () => {
  // If we're leaving an article page, close the session
  if (!isArticleDetail.value && sessionId.value) {
    try {
      await apiRequest(`/api/chat/session/${sessionId.value}`, {
        method: "DELETE"
      });
      console.log(`Chat session closed: ${sessionId.value}`);
    } catch (err) {
      console.error("Failed to close session:", err.message);
    }
    sessionId.value = null;
    messages.value = [];
    return;
  }

  // If we're entering an article page, create a new session
  if (isArticleDetail.value && articleId.value && !sessionId.value) {
    sessionCreating.value = true;
    try {
      // Fetch article for context
      const article = await apiRequest(`/api/articles/${articleId.value}`, { method: "GET" });
      const response = await apiRequest("/api/chat/session", {
        method: "POST",
        body: JSON.stringify({
          article_id: articleId.value,
          article_title: article?.title || "",
          article_content: article?.content || "",
          sources: article?.sources || []
        })
      });
      sessionId.value = response.session_id;
      // Fetch article title for greeting
      await addInitialGreeting(articleId.value);
      console.log(`Chat session created: ${sessionId.value} for article ${articleId.value}`);
    } catch (err) {
      console.error("Failed to create chat session:", err.message);
      console.error("Error details:", err);
    } finally {
      sessionCreating.value = false;
    }
  }
});

// Create a new chat session when component mounts on ArticleDetail
onMounted(async () => {
  if (isArticleDetail.value && articleId.value && !sessionId.value) {
    sessionCreating.value = true;
    try {
      // Fetch article for context
      const article = await apiRequest(`/api/articles/${articleId.value}`, { method: "GET" });
      const response = await apiRequest("/api/chat/session", {
        method: "POST",
        body: JSON.stringify({
          article_id: articleId.value,
          article_title: article?.title || "",
          article_content: article?.content || "",
          sources: article?.sources || []
        })
      });
      sessionId.value = response.session_id;
      // Fetch article title for greeting
      await addInitialGreeting(articleId.value);
      console.log(`Chat session created on mount: ${sessionId.value} for article ${articleId.value}`);
    } catch (err) {
      console.error("Failed to create chat session:", err.message);
      console.error("Error details:", err);
    } finally {
      sessionCreating.value = false;
    }
  }
});

// Close session when leaving the page
onBeforeUnmount(async () => {
  if (sessionId.value) {
    try {
      await apiRequest(`/api/chat/session/${sessionId.value}`, {
        method: "DELETE"
      });
      console.log(`Chat session closed on unmount: ${sessionId.value}`);
    } catch (err) {
      console.error("Failed to close session:", err.message);
    }
  }
});

// Helper function to fetch article title and add initial greeting
const addInitialGreeting = async (id) => {
  try {
    const article = await apiRequest(`/api/articles/${id}`, { method: "GET" });
    const title = article?.title || "this article";
    messages.value = [
      {
        role: "assistant",
        content: `Hello! I'm here to answer any questions about "${title}".`
      }
    ];
  } catch (err) {
    console.error("Failed to fetch article title for greeting:", err.message);
    // Fallback greeting if fetch fails
    messages.value = [
      {
        role: "assistant",
        content: "Hello! I'm here to answer any questions about this article."
      }
    ];
  }
};

const sendMessage = async () => {
  if (!input.value.trim() || !sessionId.value) return;

  // Add user message to chat
  messages.value.push({ role: "user", content: input.value });

  const userInput = input.value;
  input.value = "";
  isLoading.value = true;

  try {
    const res = await apiRequest("/api/chat/message", { 
      method: "POST",
      body: JSON.stringify({ 
        session_id: sessionId.value,
        message: userInput 
      })
    });
    const reply = res.response;
    messages.value.push({ role: "assistant", content: reply });
  } catch (err) {
    console.error("Chat error:", err.message);
    messages.value.push({
      role: "assistant",
      content: "Sorry, there was an error reaching the analyst.",
    });
  } finally {
    isLoading.value = false;
  }
};
</script>
