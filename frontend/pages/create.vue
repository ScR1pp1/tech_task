<template>
  <div class="min-h-screen px-4 sm:px-6 py-4 sm:py-8">
    <!-- Мобильная нижняя навигация -->
    <div class="mobile-bottom-nav">
      <NuxtLink to="/" class="flex flex-col items-center text-gray-400 hover:text-primary transition">
        <span class="text-xl mb-1">🏠</span>
        <span class="text-xs">Home</span>
      </NuxtLink>
      <button class="flex flex-col items-center text-primary" disabled>
        <span class="text-xl mb-1">✨</span>
        <span class="text-xs">Create</span>
      </button>
    </div>

    <!-- Центрированный контент -->
    <div class="max-w-4xl mx-auto">
      <!-- Навигация назад -->
      <NuxtLink to="/" class="inline-block mb-6 fade-in">
        <button class="secondary-btn text-sm px-4 py-2 flex items-center gap-2">
          <span>←</span> Back to carousels
        </button>
      </NuxtLink>

      <!-- Заголовок -->
      <header class="mb-8 fade-in text-center sm:text-left">
        <h1 class="text-3xl sm:text-4xl md:text-5xl font-black mb-2">
          <span class="gradient-text">Create</span> New Carousel
        </h1>
        <p class="text-gray-400 text-lg max-w-2xl">
          Transform your content into stunning Instagram carousels
        </p>
      </header>

      <!-- Карточка создания -->
      <div class="card p-6 sm:p-8 md:p-10 fade-in relative">
        <!-- Кнопка три точки (как на главной) -->
        <div class="absolute top-4 right-4 sm:top-6 sm:right-6 z-10">
          <button 
            class="w-10 h-10 flex items-center justify-center rounded-full hover:bg-white/5 transition text-gray-400 hover:text-white"
            @click="showMenu = !showMenu"
          >
            ⋮
          </button>
          
          <!-- Выпадающее меню -->
          <div v-if="showMenu" class="absolute right-0 mt-2 w-56 bg-slate-800 rounded-xl shadow-xl border border-white/10 z-20 overflow-hidden fade-in">
            <button class="w-full text-left px-4 py-3.5 text-sm hover:bg-white/5 transition flex items-center gap-3">
              <span class="text-lg">📋</span> 
              <span>Save as draft</span>
            </button>
            <button class="w-full text-left px-4 py-3.5 text-sm hover:bg-white/5 transition flex items-center gap-3">
              <span class="text-lg">⚙️</span> 
              <span>Settings</span>
            </button>
            <button class="w-full text-left px-4 py-3.5 text-sm text-rose-400 hover:bg-rose-500/10 transition flex items-center gap-3">
              <span class="text-lg">🗑️</span> 
              <span>Clear form</span>
            </button>
          </div>
        </div>

        <form class="flex flex-col gap-6" @submit.prevent="onSubmit">
          
          <!-- Табы выбора источника - в стиле главной -->
          <div class="scrollable-tabs pb-2 flex gap-2">
            <button 
              v-for="tab in sourceTabs" 
              :key="tab.value"
              type="button"
              :class="[
                'px-5 py-2.5 rounded-full text-sm font-medium transition-all whitespace-nowrap flex items-center gap-2',
                sourceType === tab.value 
                  ? 'bg-gradient-to-r from-primary to-secondary text-white shadow-lg' 
                  : 'bg-white/5 text-gray-400 hover:bg-white/10 border border-white/10'
              ]"
              @click="sourceType = tab.value"
            >
              <span>{{ tab.emoji }}</span>
              <span>{{ tab.label }}</span>
            </button>
          </div>

          <!-- Заголовок - в стиле главной -->
          <div class="space-y-2">
            <label class="text-sm font-medium text-gray-300 flex items-center gap-2">
              <span class="text-primary">📝</span> 
              <span>Title</span>
            </label>
            <input 
              v-model="form.title" 
              class="w-full rounded-xl px-4 py-3 bg-black/30 border border-white/10 focus:border-primary focus:ring-1 focus:ring-primary transition text-base placeholder:text-gray-600 outline-none"
              placeholder="e.g., Instagram Growth Tips"
            />
          </div>

          <!-- Source text - в стиле главной -->
          <div class="space-y-2">
            <label class="text-sm font-medium text-gray-300 flex items-center gap-2">
              <span class="text-secondary">📄</span> 
              <span>Source text</span>
            </label>
            <textarea
              v-model="form.source_text"
              rows="6"
              class="w-full rounded-xl px-4 py-3 bg-black/30 border border-white/10 focus:border-secondary focus:ring-1 focus:ring-secondary transition text-base resize-none placeholder:text-gray-600 outline-none"
              placeholder="Paste your article, ideas, or content here..."
            />
          </div>

          <!-- Настройки формата (2 колонки) - в стиле главной -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Language -->
            <div class="space-y-2">
              <label class="text-sm font-medium text-gray-300 flex items-center gap-2">
                <span class="text-emerald-400">🌍</span> 
                <span>Language</span>
              </label>
              <select v-model="form.language" class="w-full rounded-xl px-4 py-3 bg-black/30 border border-white/10 focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400 transition text-base appearance-none cursor-pointer outline-none">
                <option value="ru" class="bg-gray-900">🇷🇺 Russian</option>
                <option value="en" class="bg-gray-900">🇬🇧 English</option>
              </select>
            </div>
            
            <!-- Slides count -->
            <div class="space-y-2">
              <label class="text-sm font-medium text-gray-300 flex items-center gap-2">
                <span class="text-amber-400">🎯</span> 
                <span>Slides count</span>
              </label>
              <select v-model.number="form.slides_count" class="w-full rounded-xl px-4 py-3 bg-black/30 border border-white/10 focus:border-amber-400 focus:ring-1 focus:ring-amber-400 transition text-base cursor-pointer outline-none">
                <option v-for="n in [6,7,8,9,10]" :key="n" :value="n" class="bg-gray-900">{{ n }} slides</option>
              </select>
            </div>
          </div>

          <!-- Style hint - в стиле главной -->
          <div class="space-y-2">
            <label class="text-sm font-medium text-gray-300 flex items-center gap-2">
              <span class="text-purple-400">🎨</span> 
              <span>Style hint</span>
              <span class="text-gray-500 text-xs">(optional)</span>
            </label>
            <textarea
              v-model="form.style_hint"
              rows="3"
              class="w-full rounded-xl px-4 py-3 bg-black/30 border border-white/10 focus:border-purple-400 focus:ring-1 focus:ring-purple-400 transition text-base resize-none placeholder:text-gray-600 outline-none"
              placeholder="e.g., short, bold, with emojis, for Instagram..."
            />
          </div>

          <!-- Оценка токенов - в стиле главной -->
          <div v-if="tokenEstimate" class="bg-gradient-to-br from-primary/10 via-secondary/5 to-purple-500/10 rounded-xl p-5 border border-primary/20">
            <div class="flex items-center justify-between mb-3">
              <span class="text-sm font-medium text-gray-300 flex items-center gap-2">
                <span class="text-xl">💰</span> 
                <span>Estimated cost</span>
              </span>
              <span class="text-xs px-2 py-1 bg-black/30 rounded-full text-gray-400 border border-white/10">
                {{ tokenEstimate.model }}
              </span>
            </div>
            
            <div class="grid grid-cols-2 gap-3 mb-3">
              <div class="bg-black/30 rounded-lg p-3">
                <div class="text-xs text-gray-400 mb-1">Input tokens</div>
                <div class="text-lg font-bold text-primary-light">{{ tokenEstimate.estimated_input_tokens }}</div>
              </div>
              <div class="bg-black/30 rounded-lg p-3">
                <div class="text-xs text-gray-400 mb-1">Output tokens</div>
                <div class="text-lg font-bold text-secondary">{{ tokenEstimate.estimated_output_tokens }}</div>
              </div>
            </div>
            
            <div class="flex items-center justify-between pt-3 border-t border-white/10">
              <span class="text-sm text-gray-300">Total cost</span>
              <div class="text-right">
                <span class="text-xl font-bold gradient-text">${{ tokenEstimate.estimated_cost_usd.toFixed(4) }}</span>
                <span class="text-xs text-gray-500 ml-1">USD</span>
              </div>
            </div>
          </div>

          <!-- Скелетон загрузки -->
          <div v-else-if="estimating" class="bg-white/5 rounded-xl p-5 border border-white/10 animate-pulse">
            <div class="h-4 bg-white/10 rounded w-2/3 mb-3"></div>
            <div class="grid grid-cols-2 gap-3 mb-3">
              <div class="h-14 bg-white/10 rounded-lg"></div>
              <div class="h-14 bg-white/10 rounded-lg"></div>
            </div>
            <div class="h-10 bg-white/10 rounded-lg"></div>
          </div>

          <!-- Ошибка -->
          <p v-if="error" class="text-sm text-rose-400 bg-rose-500/10 border border-rose-500/20 rounded-lg p-3">
            {{ error }}
          </p>

          <!-- Кнопки действий - в стиле главной -->
          <div class="flex flex-col sm:flex-row gap-3 mt-4">
            <button 
              type="button"
              class="secondary-btn flex-1 py-3.5 text-base font-medium"
              @click="router.push('/')"
            >
              Cancel
            </button>
            <button 
              class="primary-btn flex-1 py-3.5 text-base font-medium flex items-center justify-center gap-2"
              type="submit" 
              :disabled="submitting"
            >
              <span v-if="submitting" class="animate-spin">⚡</span>
              <span v-else>✨</span>
              <span>{{ submitting ? 'Generating...' : 'Generate Carousel' }}</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Подсказки - 3 колонки в стиле главной -->
      <div class="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4 fade-in">
        <div class="card p-5 text-center hover:border-primary/30 transition-all group">
          <div class="text-3xl mb-2 group-hover:scale-110 transition-transform">📝</div>
          <h3 class="font-semibold mb-1">Paste any text</h3>
          <p class="text-xs text-gray-400">Articles, ideas, or bullet points</p>
        </div>
        <div class="card p-5 text-center hover:border-secondary/30 transition-all group">
          <div class="text-3xl mb-2 group-hover:scale-110 transition-transform">🎨</div>
          <h3 class="font-semibold mb-1">Customize style</h3>
          <p class="text-xs text-gray-400">Add style hints for better results</p>
        </div>
        <div class="card p-5 text-center hover:border-purple-400/30 transition-all group">
          <div class="text-3xl mb-2 group-hover:scale-110 transition-transform">⚡</div>
          <h3 class="font-semibold mb-1">AI-powered</h3>
          <p class="text-xs text-gray-400">Generates slides in seconds</p>
        </div>
      </div>
    </div>

    <!-- Оверлей для меню -->
    <div v-if="showMenu" class="fixed inset-0 z-10" @click="showMenu = false"></div>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const router = useRouter()

// Menu state
const showMenu = ref(false)

const sourceTabs = [
  { value: 'text', label: 'Text', emoji: '📝' },
  { value: 'video', label: 'Video', emoji: '🎥' },
  { value: 'links', label: 'Links', emoji: '🔗' }
]

const sourceType = ref('text')

const form = reactive({
  title: 'New carousel',
  source_text: '',
  language: 'ru',
  slides_count: 8,
  style_hint: ''
})

const submitting = ref(false)
const error = ref('')

// Token estimate
interface TokenEstimate {
  estimated_input_tokens: number
  estimated_output_tokens: number
  total_tokens: number
  estimated_cost_usd: number
  model: string
  details: any
}

const estimating = ref(false)
const tokenEstimate = ref<TokenEstimate | null>(null)
const debounceTimer = ref<NodeJS.Timeout>()

const refreshEstimate = async () => {
  if (!form.source_text && !form.style_hint) return
  
  estimating.value = true
  try {
    const { data } = await api.post('/generations/token-estimate', {
      source_text: form.source_text,
      slides_count: form.slides_count,
      language: form.language,
      style_hint: form.style_hint
    })
    tokenEstimate.value = data
  } catch (e) {
    console.error('Failed to get token estimate:', e)
  } finally {
    estimating.value = false
  }
}

// Debounced обновление
watch(
  () => [form.source_text, form.slides_count, form.language, form.style_hint],
  () => {
    clearTimeout(debounceTimer.value)
    debounceTimer.value = setTimeout(refreshEstimate, 500)
  },
  { deep: true }
)

// Получить оценку при монтировании
onMounted(() => {
  refreshEstimate()
})

const onSubmit = async () => {
  submitting.value = true
  error.value = ''
  try {
    const carouselPayload = {
      title: form.title,
      language: form.language,
      slides_count: form.slides_count,
      style_hint: form.style_hint,
      source_type: sourceType.value,
      source_payload: {
        source_text: form.source_text
      }
    }
    const { data: created } = await api.post('/carousels', carouselPayload)
    const { data: gen } = await api.post('/generations', { carousel_id: created.id })
    await router.push(`/editor/${created.id}?generationId=${gen.id}`)
  } catch (e: any) {
    error.value = e?.message || 'Failed to create carousel'
  } finally {
    submitting.value = false
  }
}
</script>