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
              :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
            >
              <div
                :class="[
                  'px-4 py-2 rounded-lg text-sm max-w-[85%] break-words',
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
/**
 * ChatWidget Component
 * 
 * A collapsible chat interface that appears on article detail pages.
 * Manages chat sessions, conversation history, and real-time messaging
 * with an AI analyst focused on the current article's content.
 * 
 * Features:
 * - Auto-creates chat session when navigating to an article page
 * - Auto-closes session when navigating away
 * - Maintains conversation history tied to backend session
 * - Displays initial greeting with article title
 * - Handles loading states during session creation and messaging
 */
import { ref, onMounted, computed, watch } from "vue";
import { useRoute } from "vue-router";
import { apiRequest } from "@/utils/api";

const route = useRoute();

/** Whether the chat widget is expanded or collapsed */
const isOpen = ref(false);

/** Current user input in the message field */
const input = ref("");

/** Array of message objects with role ('user' or 'assistant') and content */
const messages = ref([]);

/** Current session ID (UUID) for backend session tracking */
const sessionId = ref(null);

/** Whether a message is currently being sent */
const isLoading = ref(false);

/** Whether a session is currently being created */
const sessionCreating = ref(false);

/**
 * Check if we're currently on an article detail page
 * @returns {boolean} True if current route matches /articles/:id pattern
 */
const isArticleDetail = computed(() => {
  // More reliable check - just check if URL matches pattern
  const matches = route.path.match(/^\/articles\/\d+$/);
  return !!matches;
});

/**
 * Extract article ID from the current route
 * @returns {number|null} Article ID if on article page, null otherwise
 */
const articleId = computed(() => {
  const match = route.path.match(/^\/articles\/(\d+)$/);
  return match ? parseInt(match[1], 10) : null;
});

/**
 * Watch for route changes to manage session lifecycle
 * - Closes session when leaving an article page
 * - Creates session when entering an article page
 */
watch([isArticleDetail, articleId], async () => {
  // If we're leaving an article page, close the session
  if (!isArticleDetail.value && sessionId.value) {
    await closeSession();
    return;
  }

  // If we're entering an article page, create a new session
  if (isArticleDetail.value && articleId.value && !sessionId.value) {
    await createSession(articleId.value);
  }
});

/**
 * Create a chat session on component mount if on an article page
 * Ensures session is ready when user first visits an article
 */
onMounted(async () => {
  if (isArticleDetail.value && articleId.value && !sessionId.value) {
    await createSession(articleId.value);
  }
});

/**
 * Create a chat session and initialize with article context
 * 
 * Fetches the full article data and sends it to the backend to create
 * a session. The backend returns the session ID and initial greeting
 * message which is displayed in the chat.
 * 
 * @param {number} id - The article ID to create a session for
 */
const createSession = async (id) => {
  sessionCreating.value = true;
  try {
    // Fetch article for context
    const article = await apiRequest(`/api/articles/${id}`, { method: "GET" });
    const response = await apiRequest("/api/chat/session", {
      method: "POST",
      body: JSON.stringify({
        article_id: id,
        article_title: article?.title || "",
        article_content: article?.content || "",
        sources: article?.sources || [],
        tags: article?.tags || [],
        impact_score: article?.impact_score || null
      })
    });
    sessionId.value = response.session_id;
    // Use the initial messages (greeting) returned from the backend
    messages.value = response.messages || [];
    console.log(`Chat session created: ${sessionId.value} for article ${id}`);
  } catch (err) {
    console.error("Failed to create chat session:", err.message);
    console.error("Error details:", err);
    // Set fallback greeting on error
    messages.value = [
      {
        role: "assistant",
        content: "Hello! I'm here to answer any questions about this article."
      }
    ];
  } finally {
    sessionCreating.value = false;
  }
};

/**
 * Close the current chat session and clear local state
 * 
 * Sends a DELETE request to the backend to terminate the session
 * and remove it from memory. Clears the local session ID and messages.
 */
const closeSession = async () => {
  if (sessionId.value) {
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
  }
};

/**
 * Send a user message to the chat backend and display the response
 * 
 * Validates input, adds the user message to the UI immediately,
 * sends it to the backend with the session ID, and appends the
 * AI response to the conversation when received.
 */
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