<template>
  <!-- Only show chat widget on article detail pages -->
  <div v-if="isArticleDetail" class="fixed bottom-6 right-8 w-80 z-50">
    <!-- Collapsed Chat Button and Chat Box Container -->
    <div class="relative w-full h-full">
      <!-- Collapsed Chat Button -->
      <transition
        name="button-fade"
        mode="out-in"
      >
        <button
          v-if="!isOpen && sessionId"
          key="button"
          @click="isOpen = true"
          class="bg-blue-600 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg hover:bg-blue-700 transition absolute bottom-0 right-0"
        >
          💬
        </button>

        <!-- Loading button while creating session -->
        <button
          v-else-if="!isOpen && sessionCreating"
          key="loading"
          disabled
          class="bg-slate-600 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg cursor-not-allowed absolute bottom-0 right-0"
        >
          ⏳
        </button>
      </transition>

      <!-- Chat Box with Transition -->
      <transition
        name="chat-slide"
      >
        <div
          v-if="isOpen && sessionId"
          class="bg-slate-800 shadow-xl h-144 rounded-2xl flex flex-col border border-slate-700 absolute bottom-0 right-0 w-80"
        >
          <div class="bg-gradient-to-r from-blue-600 to-blue-700 rounded-t-2xl text-white p-4 flex justify-between items-center">
            <h3 class="font-semibold">Ask the Analyst</h3>
            <button @click="isOpen = false" class="text-white hover:text-slate-200 transition">✕</button>
          </div>

          <div class="flex-1 p-4 overflow-y-auto h-64 space-y-3">
            <div
              v-for="(msg, idx) in messages"
              :key="idx"
              :class="msg.role === 'user' ? 'text-right' : 'text-left'"
            >
              <div
                :class="[
                  'inline-block px-4 py-2 rounded-lg text-sm',
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-slate-100'
                ]"
              >
                {{ msg.content }}
              </div>
            </div>
          </div>

          <form @submit.prevent="sendMessage" class="p-4 border-t border-slate-700 flex gap-2">
            <input
              v-model="input"
              type="text"
              placeholder="Ask a question..."
              :disabled="isLoading"
              class="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            />
            <button
              type="submit"
              :disabled="isLoading || !input.trim()"
              class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-slate-600 transition"
            >
              {{ isLoading ? "..." : "→" }}
            </button>
          </form>
        </div>
      </transition>
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

<style scoped>
.button-fade-enter-active,
.button-fade-leave-active {
  transition: opacity 0.3s ease;
}

.button-fade-enter-from,
.button-fade-leave-to {
  opacity: 0;
}

.chat-slide-enter-active {
  transition: all 0.3s ease-out;
  transform-origin: bottom right;
}

.chat-slide-leave-active {
  transition: all 0.3s ease-in;
  transform-origin: bottom right;
}

.chat-slide-enter-from {
  opacity: 0;
  transform: scale(0) translateY(0);
}

.chat-slide-leave-to {
  opacity: 0;
  transform: scale(0) translateY(0);
}

.chat-slide-enter-to,
.chat-slide-leave-from {
  opacity: 1;
  transform: scale(1) translateY(0);
}
</style>