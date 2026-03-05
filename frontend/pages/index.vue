<template>
  <div class="page-container">
    <div class="min-h-screen px-4 sm:px-6 py-4 sm:py-8">
      <!-- Мобильная нижняя навигация -->
      <div class="mobile-bottom-nav">
        <button class="flex flex-col items-center text-primary" disabled>
          <span class="text-xl mb-1">🏠</span>
          <span class="text-xs">Home</span>
        </button>
        <NuxtLink to="/create" class="flex flex-col items-center text-gray-400 hover:text-primary transition">
          <span class="text-xl mb-1">✨</span>
          <span class="text-xs">Create</span>
        </NuxtLink>
        <button class="flex flex-col items-center text-gray-400" disabled>
          <span class="text-xl mb-1">⚙️</span>
          <span class="text-xs">Settings</span>
        </button>
      </div>

      <!-- Хедер -->
      <header class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8 sm:mb-12 fade-in">
        <div>
          <h1 class="text-3xl sm:text-4xl md:text-5xl font-black mb-2">
            <span class="gradient-text">Carousel</span> Studio
          </h1>
          <p class="text-gray-400 text-sm sm:text-base">
            Create stunning Instagram carousels with AI
          </p>
        </div>
        
        <!-- Десктопная кнопка -->
        <NuxtLink to="/create" class="hidden sm:block">
          <button class="primary-btn text-base px-6 py-3 flex items-center gap-2">
            <span class="text-xl">✨</span>
            New Carousel
          </button>
        </NuxtLink>
        
        <!-- Мобильная кнопка (плавающая) -->
        <NuxtLink to="/create" class="sm:hidden fixed bottom-20 right-4 z-50">
          <button class="primary-btn w-14 h-14 rounded-full flex items-center justify-center text-2xl shadow-lg">
            ✨
          </button>
        </NuxtLink>
      </header>

      <!-- Состояния загрузки -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20 fade-in">
        <div class="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
        <p class="text-gray-400">Loading your creations...</p>
      </div>

      <!-- Пустое состояние -->
      <div v-else-if="carousels.length === 0" class="text-center py-20 fade-in">
        <div class="text-8xl mb-6 opacity-30">🎨</div>
        <h2 class="text-2xl font-bold mb-3">No carousels yet</h2>
        <p class="text-gray-400 mb-8 max-w-md mx-auto">
          Create your first carousel and start generating amazing content for Instagram
        </p>
        <NuxtLink to="/create" class="sm:hidden">
          <button class="primary-btn text-base px-8 py-3">
            Create First Carousel
          </button>
        </NuxtLink>
      </div>

      <!-- Сетка каруселей -->
      <div v-else class="grid-responsive fade-in">
        <div v-for="c in carousels" :key="c.id" class="card group">
          <!-- Превью -->
          <div class="relative aspect-[4/5] rounded-2xl overflow-hidden mb-4 bg-gradient-to-br from-primary/20 to-secondary/20">
            <img 
              v-if="c.previewUrl" 
              :src="`${config.public.apiBase}/preview/${c.id}?t=${Date.now()}`" 
              :alt="c.title"
              class="w-full h-full object-cover transition-transform group-hover:scale-105"
              @error="handleImageError"
            />
            <div v-else class="w-full h-full flex items-center justify-center">
              <span class="text-6xl opacity-30">🖼️</span>
            </div>
            
            <!-- Статус -->
            <span :class="['status-pill absolute top-3 right-3', getStatusClass(c.status)]">
              {{ c.status }}
            </span>
          </div>

          <!-- Информация -->
          <div class="flex items-start justify-between gap-3 mb-4">
            <div class="min-w-0 flex-1">
              <h3 class="font-bold text-lg truncate mb-1">{{ c.title }}</h3>
              <div class="flex items-center gap-2 text-xs text-gray-400">
                <span>{{ formatDate(c.created_at) }}</span>
                <span>•</span>
                <span>{{ c.language.toUpperCase() }}</span>
                <span>•</span>
                <span>{{ c.slides_count }} slides</span>
              </div>
            </div>
            
            <!-- Меню с тремя точками -->
            <div class="relative">
              <button 
                class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/5 transition"
                @click="toggleMenu(c.id)"
              >
                ⋮
              </button>
              
              <!-- Выпадающее меню -->
              <div v-if="activeMenuId === c.id" class="absolute right-0 mt-2 w-48 bg-slate-800 rounded-xl shadow-xl border border-white/10 z-10 overflow-hidden fade-in">
                <button 
                  class="w-full text-left px-4 py-3 text-sm hover:bg-white/5 transition flex items-center gap-2"
                  @click="duplicateCarousel(c.id)"
                >
                  <span>📋</span> Duplicate
                </button>
                <button 
                  class="w-full text-left px-4 py-3 text-sm hover:bg-white/5 transition flex items-center gap-2"
                  @click="exportCarousel(c.id)"
                >
                  <span>📦</span> Export
                </button>
                <button 
                  class="w-full text-left px-4 py-3 text-sm text-rose-400 hover:bg-rose-500/10 transition flex items-center gap-2"
                  @click="confirmDelete(c.id)"
                >
                  <span>🗑️</span> Delete
                </button>
              </div>
            </div>
          </div>

          <!-- Кнопка открыть -->
          <NuxtLink :to="`/editor/${c.id}`">
            <button class="secondary-btn w-full text-sm py-2.5 hover:border-primary/50 transition">
              Open Editor →
            </button>
          </NuxtLink>
        </div>
      </div>

      <!-- Мобильный оверлей для меню -->
      <div v-if="activeMenuId" class="fixed inset-0 z-40" @click="activeMenuId = null"></div>
    </div>

    <!-- Модалка подтверждения удаления -->
    <Teleport to="body">
      <div v-if="showDeleteModal" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" @click="showDeleteModal = false">
        <div class="bg-slate-800 rounded-2xl p-6 max-w-sm w-full fade-in" @click.stop>
          <div class="text-center mb-4">
            <div class="text-5xl mb-4">🗑️</div>
            <h3 class="text-xl font-bold mb-2">Delete Carousel?</h3>
            <p class="text-gray-400 text-sm">This action cannot be undone.</p>
          </div>
          <div class="flex gap-3">
            <button class="secondary-btn flex-1 py-3" @click="showDeleteModal = false">Cancel</button>
            <button class="primary-btn flex-1 py-3 bg-rose-600 hover:bg-rose-700" @click="deleteCarousel">
              Delete
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
// Импорты
const api = useApi()
const config = useRuntimeConfig()
const router = useRouter()

// Типы
type Carousel = {
  id: number
  title: string
  created_at: string
  status: string
  language: string
  slides_count: number
  previewUrl?: string
}

// Состояния
const carousels = ref<Carousel[]>([])
const loading = ref(true)
const activeMenuId = ref<number | null>(null)

// Delete состояния
const showDeleteModal = ref(false)
const carouselToDelete = ref<number | null>(null)

// Получение данных
const fetchCarousels = async () => {
  loading.value = true
  try {
    const { data } = await api.get<Carousel[]>('/carousels')
    carousels.value = data.map(c => ({
      ...c,
      previewUrl: c.status === 'ready' ? `/api/preview/${c.id}` : undefined
    }))
  } catch (error) {
    console.error('Failed to fetch carousels:', error)
  } finally {
    loading.value = false
  }
}

// Форматирование даты
const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}

// Класс статуса
const getStatusClass = (status: string) => {
  if (status === 'ready') return 'status-ready'
  if (status === 'generating') return 'status-generating'
  if (status === 'failed') return 'status-failed'
  return 'status-draft'
}

// Меню
const toggleMenu = (id: number) => {
  activeMenuId.value = activeMenuId.value === id ? null : id
}

// Delete
const confirmDelete = (id: number) => {
  carouselToDelete.value = id
  showDeleteModal.value = true
  activeMenuId.value = null
}

const deleteCarousel = async () => {
  if (!carouselToDelete.value) return
  
  try {
    await api.delete(`/carousels/${carouselToDelete.value}`)
    carousels.value = carousels.value.filter(c => c.id !== carouselToDelete.value)
    showDeleteModal.value = false
    carouselToDelete.value = null
  } catch (e: any) {
    console.error('Failed to delete:', e)
    alert('Failed to delete carousel: ' + (e?.message || 'Unknown error'))
  }
}

// Duplicate
const duplicateCarousel = async (id: number) => {
  try {
    const { data: original } = await api.get(`/carousels/${id}`)
    
    const copyPayload = {
      title: `${original.title} (copy)`,
      language: original.language,
      slides_count: original.slides_count,
      style_hint: original.style_hint,
      source_type: original.source_type,
      source_payload: original.source_payload,
      design: original.design
    }
    
    const { data: newCarousel } = await api.post('/carousels', copyPayload)
    
    if (original.status === 'ready') {
      await api.post('/generations', { carousel_id: newCarousel.id })
    }
    
    await fetchCarousels()
    activeMenuId.value = null
  } catch (e: any) {
    console.error('Failed to duplicate:', e)
    alert('Failed to duplicate carousel: ' + (e?.message || 'Unknown error'))
  }
}

// Export
const exportCarousel = async (id: number) => {
  try {
    const { data } = await api.post('/exports', { carousel_id: id })
    window.open(`/editor/${id}?exportId=${data.id}`, '_blank')
    activeMenuId.value = null
  } catch (e: any) {
    console.error('Failed to export:', e)
    alert('Failed to export carousel: ' + (e?.message || 'Unknown error'))
  }
}

// Image error handler
const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}

// Инициализация
onMounted(fetchCarousels)
</script>