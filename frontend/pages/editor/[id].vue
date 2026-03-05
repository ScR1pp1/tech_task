<template>
  <!-- Мобильная нижняя навигация -->
  <div class="mobile-bottom-nav sm:hidden">
    <button 
      class="flex flex-col items-center" 
      :class="mobileTab === 'editor' ? 'text-emerald-400' : 'text-slate-400'"
      @click="mobileTab = 'editor'"
    >
      <span class="text-xl mb-1">✏️</span>
      <span class="text-xs">Editor</span>
    </button>
    <button 
      class="flex flex-col items-center" 
      :class="mobileTab === 'design' ? 'text-emerald-400' : 'text-slate-400'"
      @click="mobileTab = 'design'"
    >
      <span class="text-xl mb-1">🎨</span>
      <span class="text-xs">Design</span>
    </button>
    <button 
      class="flex flex-col items-center" 
      :class="mobileTab === 'history' ? 'text-emerald-400' : 'text-slate-400'"
      @click="mobileTab = 'history'"
    >
      <span class="text-xl mb-1">📋</span>
      <span class="text-xs">History</span>
    </button>
  </div>

  <!-- Основной контейнер -->
  <div class="min-h-screen px-3 sm:px-4 py-4 sm:py-6 max-w-6xl mx-auto">
    <!-- Кнопка назад -->
    <NuxtLink to="/">
      <button class="secondary-btn text-xs mb-4 sm:mb-6 px-3 sm:px-4">
        <span class="sm:hidden">←</span>
        <span class="hidden sm:inline">&larr; Back</span>
      </button>
    </NuxtLink>

    <!-- Десктопная версия (2 колонки) -->
    <div v-if="!isMobile || mobileTab === 'editor'" class="grid gap-4 md:grid-cols-[2fr_1fr]">
      <!-- Левая колонка - редактор слайдов -->
      <div>
        <!-- Заголовок и кнопка экспорта -->
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-3">
          <div>
            <h1 class="text-lg sm:text-xl font-semibold">{{ carousel?.title }}</h1>
            <p class="text-xs text-slate-400">
              {{ carousel?.language?.toUpperCase() }} · {{ carousel?.slides_count }} slides
            </p>
          </div>
          <button class="primary-btn text-xs sm:text-sm px-3 sm:px-4 py-2" @click="onExport" :disabled="exporting">
            {{ exporting ? 'Preparing ZIP...' : 'Export PNG/ZIP' }}
          </button>
        </div>

        <!-- Навигация по слайдам -->
        <div class="scrollable-tabs mb-4">
          <button
            v-for="s in slides"
            :key="s.id"
            :class="['status-pill text-xs border px-3 py-1.5 whitespace-nowrap', 
                     s.id === activeSlideId ? 'bg-slate-100 text-slate-900' : 'bg-slate-900 border-slate-600']"
            @click="activeSlideId = s.id"
          >
            Slide {{ s.order }}
          </button>
        </div>

        <!-- Слайд для редактирования (canvas) -->
        <div v-if="activeSlide" class="card flex items-center justify-center overflow-auto">
          <div
            ref="slideDom"
            class="flex flex-col"
            :style="slideCanvasStyle"
          >
            <!-- Header (если включен) -->
            <div v-if="design.showHeader" class="w-full mb-4">
              <input
                v-model="activeSlide.title"
                class="w-full bg-transparent text-4xl font-black mb-6 border-none outline-none placeholder:text-white/20"
                :class="{'text-white': design.bgColor === '#020617'}"
                placeholder="Title"
              />
            </div>

            <!-- Основной контент -->
            <div class="w-full flex-1">
              <input
                v-model="activeSlide.title"
                class="w-full bg-transparent font-semibold mb-3 border-none outline-none"
                :class="{'text-white': design.bgColor === '#020617'}"
                :style="{ fontSize: design.titleFontSize + 'px', fontFamily: design.fontFamily, textAlign: design.alignment }"
                @blur="saveActive"
              />
              <textarea
                v-model="activeSlide.body"
                rows="8"
                class="w-full bg-transparent text-xl leading-relaxed resize-none border-none outline-none placeholder:text-white/20"
                :class="{'text-white': design.bgColor === '#020617'}"
                placeholder="Write your content here..."
              />
            </div>

            <!-- Footer (если включен) -->
            <div v-if="design.showFooter" class="w-full mt-4">
              <input
                v-model="activeSlide.footer"
                placeholder="Call to action"
                class="w-full bg-transparent text-sm text-white/60 border-none outline-none placeholder:text-white/20"
              />
            </div>
          </div>
        </div>

        <!-- Статус генерации -->
        <p v-if="genStatusText" class="text-xs text-slate-400 mt-3">
          Generation: {{ genStatusText }}
        </p>
      </div>

      <!-- Правая колонка - настройки (десктоп) -->
      <aside class="space-y-4 hidden md:block">
        <!-- НОВАЯ СЕКЦИЯ ДИЗАЙНА С ТАБАМИ -->
        <div class="card">
          <h2 class="text-sm font-semibold mb-3 flex items-center justify-between">
            <span>Design settings</span>
            <span class="text-xs text-slate-500">{{ design.template }} template</span>
          </h2>
          
          <!-- Tabs for design categories -->
          <div class="flex gap-1 mb-4 border-b border-slate-700">
            <button 
              v-for="tab in designTabs" 
              :key="tab.id"
              :class="['px-3 py-1.5 text-xs font-medium rounded-t-lg -mb-px', 
                       activeDesignTab === tab.id ? 'text-emerald-400 border-b-2 border-emerald-400' : 'text-slate-400']"
              @click="activeDesignTab = tab.id"
            >
              {{ tab.label }}
            </button>
          </div>
          
          <!-- Template Tab -->
          <div v-if="activeDesignTab === 'template'" class="space-y-4">
            <div>
              <label class="block text-xs mb-2">Template style</label>
              <div class="grid grid-cols-3 gap-2">
                <button 
                  v-for="t in templates" 
                  :key="t.id"
                  :class="['p-2 rounded-lg border text-xs transition-all', 
                           design.template === t.id ? 'border-emerald-500 bg-emerald-950/30' : 'border-slate-700 hover:border-slate-500']"
                  @click="design.template = t.id"
                >
                  <div class="aspect-[4/5] rounded mb-1" :style="{ background: t.preview }"></div>
                  <span class="block text-center">{{ t.name }}</span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Background Tab -->
          <div v-if="activeDesignTab === 'background'" class="space-y-4">
            <!-- Color picker -->
            <div>
              <label class="block text-xs mb-2">Background color</label>
              <div class="flex gap-2">
                <input 
                  v-model="design.bgColor" 
                  type="color" 
                  class="w-12 h-12 rounded-md border border-slate-700 cursor-pointer"
                />
                <input 
                  v-model="design.bgColor" 
                  type="text" 
                  class="flex-1 rounded-md px-3 py-2 bg-slate-900 border border-slate-700 text-xs font-mono"
                  placeholder="#020617"
                />
              </div>
            </div>
            
            <!-- Preset colors -->
            <div>
              <label class="block text-xs mb-2">Presets</label>
              <div class="flex flex-wrap gap-2">
                <button 
                  v-for="color in colorPresets" 
                  :key="color"
                  class="w-8 h-8 rounded-full border-2 transition-all"
                  :class="design.bgColor === color ? 'border-white scale-110' : 'border-transparent'"
                  :style="{ backgroundColor: color }"
                  @click="design.bgColor = color"
                />
              </div>
            </div>
            
            <!-- Background image -->
            <div>
              <label class="block text-xs mb-2">Background image</label>
              <div class="flex flex-col gap-2">
                <div 
                  v-if="design.bgImageUrl" 
                  class="relative aspect-video rounded-lg overflow-hidden border border-slate-700"
                >
                  <img :src="design.bgImageUrl" class="w-full h-full object-cover" />
                  <button 
                    class="absolute top-2 right-2 bg-rose-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs"
                    @click="design.bgImageUrl = ''"
                  >
                    ✕
                  </button>
                </div>
                
                <label class="cursor-pointer">
                  <input 
                    type="file" 
                    accept="image/*" 
                    @change="onUploadBg" 
                    class="hidden"
                  />
                  <div class="border-2 border-dashed border-slate-700 rounded-lg p-4 text-center hover:border-emerald-500 transition-colors">
                    <span class="text-xs text-slate-400">Click to upload image</span>
                  </div>
                </label>
                
                <!-- Opacity slider -->
                <div v-if="design.bgImageUrl" class="mt-2">
                  <label class="block text-xs mb-2">Overlay opacity</label>
                  <input 
                    v-model.number="design.overlayOpacity" 
                    type="range" 
                    min="0" 
                    max="100" 
                    class="w-full accent-emerald-500"
                  />
                  <div class="flex justify-between text-xs text-slate-500 mt-1">
                    <span>0%</span>
                    <span>{{ design.overlayOpacity || 50 }}%</span>
                    <span>100%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Layout Tab -->
          <div v-if="activeDesignTab === 'layout'" class="space-y-4">
            <!-- Padding -->
            <div>
              <label class="block text-xs mb-2">Content padding</label>
              <input 
                v-model.number="design.padding" 
                type="range" 
                min="40" 
                max="120" 
                step="10"
                class="w-full accent-emerald-500"
              />
              <div class="flex justify-between text-xs text-slate-500 mt-1">
                <span>Compact</span>
                <span>{{ design.padding || 80 }}px</span>
                <span>Spacious</span>
              </div>
            </div>
            
            <!-- Alignment -->
            <div>
              <label class="block text-xs mb-2">Text alignment</label>
              <div class="flex gap-2">
                <button 
                  v-for="align in ['left', 'center', 'right']" 
                  :key="align"
                  :class="['flex-1 py-2 rounded border text-xs', 
                           design.alignment === align ? 'border-emerald-500 bg-emerald-950/30' : 'border-slate-700']"
                  @click="design.alignment = align"
                >
                  {{ align }}
                </button>
              </div>
            </div>
            
            <!-- Vertical alignment -->
            <div>
              <label class="block text-xs mb-2">Vertical alignment</label>
              <div class="flex gap-2">
                <button 
                  v-for="valign in ['top', 'center', 'bottom']" 
                  :key="valign"
                  :class="['flex-1 py-2 rounded border text-xs', 
                           design.valign === valign ? 'border-emerald-500 bg-emerald-950/30' : 'border-slate-700']"
                  @click="design.valign = valign"
                >
                  {{ valign }}
                </button>
              </div>
            </div>
          </div>
          
          <!-- Header/Footer Tab -->
          <div v-if="activeDesignTab === 'headerfooter'" class="space-y-4">
            <!-- Header toggle -->
            <div class="flex items-center justify-between">
              <span class="text-xs">Show header</span>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="design.showHeader" class="sr-only peer">
                <div class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-600"></div>
              </label>
            </div>
            
            <div v-if="design.showHeader">
              <label class="block text-xs mb-2">Header text</label>
              <input 
                v-model="design.headerText" 
                type="text" 
                class="w-full rounded-md px-3 py-2 bg-slate-900 border border-slate-700 text-xs"
                placeholder="Header title"
              />
            </div>
            
            <!-- Footer toggle -->
            <div class="flex items-center justify-between">
              <span class="text-xs">Show footer</span>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="design.showFooter" class="sr-only peer">
                <div class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-600"></div>
              </label>
            </div>
            
            <div v-if="design.showFooter">
              <label class="block text-xs mb-2">Footer text</label>
              <input 
                v-model="design.footerText" 
                type="text" 
                class="w-full rounded-md px-3 py-2 bg-slate-900 border border-slate-700 text-xs"
                placeholder="Call to action"
              />
            </div>
          </div>
          
          <!-- Typography Tab -->
          <div v-if="activeDesignTab === 'typography'" class="space-y-4">
            <div>
              <label class="block text-xs mb-2">Title font size</label>
              <div class="flex items-center gap-2">
                <input 
                  v-model.number="design.titleFontSize" 
                  type="range" 
                  min="20" 
                  max="48" 
                  class="flex-1 accent-emerald-500"
                />
                <span class="text-xs w-12">{{ design.titleFontSize || 32 }}px</span>
              </div>
            </div>
            
            <div>
              <label class="block text-xs mb-2">Body font size</label>
              <div class="flex items-center gap-2">
                <input 
                  v-model.number="design.bodyFontSize" 
                  type="range" 
                  min="14" 
                  max="28" 
                  class="flex-1 accent-emerald-500"
                />
                <span class="text-xs w-12">{{ design.bodyFontSize || 18 }}px</span>
              </div>
            </div>
            
            <div>
              <label class="block text-xs mb-2">Font family</label>
              <select v-model="design.fontFamily" class="w-full rounded-md px-3 py-2 bg-slate-900 border border-slate-700 text-xs">
                <option value="system-ui">System UI</option>
                <option value="Inter">Inter</option>
                <option value="Roboto">Roboto</option>
                <option value="Helvetica">Helvetica</option>
                <option value="Georgia">Georgia</option>
              </select>
            </div>
          </div>
          
          <!-- Apply buttons -->
          <div class="flex gap-2 mt-6 pt-4 border-t border-slate-700">
            <button class="secondary-btn text-xs flex-1" @click="resetDesign">
              Reset
            </button>
            <button class="primary-btn text-xs flex-1" @click="saveDesign">
              Apply to all slides
            </button>
          </div>
        </div>
        <!-- КОНЕЦ НОВОЙ СЕКЦИИ -->

        <!-- История генераций -->
        <div class="card">
          <div class="flex items-center justify-between mb-2">
            <h2 class="text-sm font-semibold">Generations</h2>
            <button class="secondary-btn text-[10px] px-2 py-1" @click="triggerRegenerate" :disabled="regenerating">
              {{ regenerating ? 'Generating…' : 'Re-generate' }}
            </button>
          </div>
          <p v-if="!generations.length" class="text-xs text-slate-400">
            No generations yet for this carousel.
          </p>
          <ul v-else class="space-y-1 text-xs">
            <li v-for="g in generations" :key="g.id" class="flex items-center justify-between">
              <span class="text-slate-300">
                {{ new Date(g.created_at).toLocaleTimeString() }}
              </span>
              <span :class="['status-pill', statusClass(g.status)]">
                {{ g.status }}
              </span>
            </li>
          </ul>
        </div>
      </aside>
    </div>

    <!-- Мобильные версии табов -->
    <div v-if="isMobile && mobileTab === 'design'" class="mt-4">
      <aside class="space-y-4">
        <!-- Копия секции дизайна для мобильных -->
        <div class="card">
          <h2 class="text-sm font-semibold mb-3 flex items-center justify-between">
            <span>Design settings</span>
            <span class="text-xs text-slate-500">{{ design.template }} template</span>
          </h2>
          
          <!-- Tabs for design categories -->
          <div class="flex gap-1 mb-4 border-b border-slate-700">
            <button 
              v-for="tab in designTabs" 
              :key="tab.id"
              :class="['px-3 py-1.5 text-xs font-medium rounded-t-lg -mb-px', 
                       activeDesignTab === tab.id ? 'text-emerald-400 border-b-2 border-emerald-400' : 'text-slate-400']"
              @click="activeDesignTab = tab.id"
            >
              {{ tab.label }}
            </button>
          </div>
          
          <!-- Template Tab -->
          <div v-if="activeDesignTab === 'template'" class="space-y-4">
            <div>
              <label class="block text-xs mb-2">Template style</label>
              <div class="grid grid-cols-3 gap-2">
                <button 
                  v-for="t in templates" 
                  :key="t.id"
                  :class="['p-2 rounded-lg border text-xs transition-all', 
                           design.template === t.id ? 'border-emerald-500 bg-emerald-950/30' : 'border-slate-700 hover:border-slate-500']"
                  @click="design.template = t.id"
                >
                  <div class="aspect-[4/5] rounded mb-1" :style="{ background: t.preview }"></div>
                  <span class="block text-center">{{ t.name }}</span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Background Tab -->
          <div v-if="activeDesignTab === 'background'" class="space-y-4">
            <!-- Color picker -->
            <div>
              <label class="block text-xs mb-2">Background color</label>
              <div class="flex gap-2">
                <input 
                  v-model="design.bgColor" 
                  type="color" 
                  class="w-12 h-12 rounded-md border border-slate-700 cursor-pointer"
                />
                <input 
                  v-model="design.bgColor" 
                  type="text" 
                  class="flex-1 rounded-md px-3 py-2 bg-slate-900 border border-slate-700 text-xs font-mono"
                  placeholder="#020617"
                />
              </div>
            </div>
            
            <!-- Preset colors -->
            <div>
              <label class="block text-xs mb-2">Presets</label>
              <div class="flex flex-wrap gap-2">
                <button 
                  v-for="color in colorPresets" 
                  :key="color"
                  class="w-8 h-8 rounded-full border-2 transition-all"
                  :class="design.bgColor === color ? 'border-white scale-110' : 'border-transparent'"
                  :style="{ backgroundColor: color }"
                  @click="design.bgColor = color"
                />
              </div>
            </div>
            
            <!-- Background image -->
            <div>
              <label class="block text-xs mb-2">Background image</label>
              <div class="flex flex-col gap-2">
                <div 
                  v-if="design.bgImageUrl" 
                  class="relative aspect-video rounded-lg overflow-hidden border border-slate-700"
                >
                  <img :src="design.bgImageUrl" class="w-full h-full object-cover" />
                  <button 
                    class="absolute top-2 right-2 bg-rose-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs"
                    @click="design.bgImageUrl = ''"
                  >
                    ✕
                  </button>
                </div>
                
                <label class="cursor-pointer">
                  <input 
                    type="file" 
                    accept="image/*" 
                    @change="onUploadBg" 
                    class="hidden"
                  />
                  <div class="border-2 border-dashed border-slate-700 rounded-lg p-4 text-center hover:border-emerald-500 transition-colors">
                    <span class="text-xs text-slate-400">Click to upload image</span>
                  </div>
                </label>
                
                <!-- Opacity slider -->
                <div v-if="design.bgImageUrl" class="mt-2">
                  <label class="block text-xs mb-2">Overlay opacity</label>
                  <input 
                    v-model.number="design.overlayOpacity" 
                    type="range" 
                    min="0" 
                    max="100" 
                    class="w-full accent-emerald-500"
                  />
                  <div class="flex justify-between text-xs text-slate-500 mt-1">
                    <span>0%</span>
                    <span>{{ design.overlayOpacity || 50 }}%</span>
                    <span>100%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Layout Tab -->
          <div v-if="activeDesignTab === 'layout'" class="space-y-4">
            <!-- Padding -->
            <div>
              <label class="block text-xs mb-2">Content padding</label>
              <input 
                v-model.number="design.padding" 
                type="range" 
                min="40" 
                max="120" 
                step="10"
                class="w-full accent-emerald-500"
              />
              <div class="flex justify-between text-xs text-slate-500 mt-1">
                <span>Compact</span>
                <span>{{ design.padding || 80 }}px</span>
                <span>Spacious</span>
              </div>
            </div>
            
            <!-- Alignment -->
            <div>
              <label class="block text-xs mb-2">Text alignment</label>
              <div class="flex gap-2">
                <button 
                  v-for="align in ['left', 'center', 'right']" 
                  :key="align"
                  :class="['flex-1 py-2 rounded border text-xs', 
                           design.alignment === align ? 'border-emerald-500 bg-emerald-950/30' : 'border-slate-700']"
                  @click="design.alignment = align"
                >
                  {{ align }}
                </button>
              </div>
            </div>
            
            <!-- Vertical alignment -->
            <div>
              <label class="block text-xs mb-2">Vertical alignment</label>
              <div class="flex gap-2">
                <button 
                  v-for="valign in ['top', 'center', 'bottom']" 
                  :key="valign"
                  :class="['flex-1 py-2 rounded border text-xs', 
                           design.valign === valign ? 'border-emerald-500 bg-emerald-950/30' : 'border-slate-700']"
                  @click="design.valign = valign"
                >
                  {{ valign }}
                </button>
              </div>
            </div>
          </div>
          
          <!-- Header/Footer Tab -->
          <div v-if="activeDesignTab === 'headerfooter'" class="space-y-4">
            <!-- Header toggle -->
            <div class="flex items-center justify-between">
              <span class="text-xs">Show header</span>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="design.showHeader" class="sr-only peer">
                <div class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-600"></div>
              </label>
            </div>
            
            <div v-if="design.showHeader">
              <label class="block text-xs mb-2">Header text</label>
              <input 
                v-model="design.headerText" 
                type="text" 
                class="w-full rounded-md px-3 py-2 bg-slate-900 border border-slate-700 text-xs"
                placeholder="Header title"
              />
            </div>
            
            <!-- Footer toggle -->
            <div class="flex items-center justify-between">
              <span class="text-xs">Show footer</span>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="design.showFooter" class="sr-only peer">
                <div class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-600"></div>
              </label>
            </div>
            
            <div v-if="design.showFooter">
              <label class="block text-xs mb-2">Footer text</label>
              <input 
                v-model="design.footerText" 
                type="text" 
                class="w-full rounded-md px-3 py-2 bg-slate-900 border border-slate-700 text-xs"
                placeholder="Call to action"
              />
            </div>
          </div>
          
          <!-- Typography Tab -->
          <div v-if="activeDesignTab === 'typography'" class="space-y-4">
            <div>
              <label class="block text-xs mb-2">Title font size</label>
              <div class="flex items-center gap-2">
                <input 
                  v-model.number="design.titleFontSize" 
                  type="range" 
                  min="20" 
                  max="48" 
                  class="flex-1 accent-emerald-500"
                />
                <span class="text-xs w-12">{{ design.titleFontSize || 32 }}px</span>
              </div>
            </div>
            
            <div>
              <label class="block text-xs mb-2">Body font size</label>
              <div class="flex items-center gap-2">
                <input 
                  v-model.number="design.bodyFontSize" 
                  type="range" 
                  min="14" 
                  max="28" 
                  class="flex-1 accent-emerald-500"
                />
                <span class="text-xs w-12">{{ design.bodyFontSize || 18 }}px</span>
              </div>
            </div>
            
            <div>
              <label class="block text-xs mb-2">Font family</label>
              <select v-model="design.fontFamily" class="w-full rounded-md px-3 py-2 bg-slate-900 border border-slate-700 text-xs">
                <option value="system-ui">System UI</option>
                <option value="Inter">Inter</option>
                <option value="Roboto">Roboto</option>
                <option value="Helvetica">Helvetica</option>
                <option value="Georgia">Georgia</option>
              </select>
            </div>
          </div>
          
          <!-- Apply buttons -->
          <div class="flex gap-2 mt-6 pt-4 border-t border-slate-700">
            <button class="secondary-btn text-xs flex-1" @click="resetDesign">
              Reset
            </button>
            <button class="primary-btn text-xs flex-1" @click="saveDesign">
              Apply to all slides
            </button>
          </div>
        </div>
      </aside>
    </div>
    
    <div v-if="isMobile && mobileTab === 'history'" class="mt-4">
      <aside class="space-y-4">
        <div class="card">
          <div class="flex items-center justify-between mb-2">
            <h2 class="text-sm font-semibold">Generations</h2>
            <button class="secondary-btn text-xs px-3 py-1" @click="triggerRegenerate" :disabled="regenerating">
              {{ regenerating ? 'Generating…' : 'Re-generate' }}
            </button>
          </div>
          <p v-if="!generations.length" class="text-xs text-slate-400">
            No generations yet for this carousel.
          </p>
          <ul v-else class="space-y-2 text-xs">
            <li v-for="g in generations" :key="g.id" class="flex items-center justify-between p-2 bg-slate-800/50 rounded">
              <div class="flex flex-col">
                <span class="text-slate-300">
                  {{ new Date(g.created_at).toLocaleString() }}
                </span>
                <span v-if="g.error" class="text-rose-400 text-[10px]">{{ g.error }}</span>
              </div>
              <span :class="['status-pill', statusClass(g.status)]">
                {{ g.status }}
              </span>
            </li>
          </ul>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import JSZip from 'jszip'
import html2canvas from 'html2canvas'
import axios from 'axios'

const route = useRoute()
const api = useApi()
const config = useRuntimeConfig()

// Мобильные переменные
const isMobile = ref(false)
const mobileTab = ref('editor')

// НОВЫЕ ПЕРЕМЕННЫЕ ДЛЯ ДИЗАЙНА
const activeDesignTab = ref('template')
const designTabs = [
  { id: 'template', label: '🎨 Template' },
  { id: 'background', label: '🌈 Background' },
  { id: 'layout', label: '📐 Layout' },
  { id: 'headerfooter', label: '📝 Header/Footer' },
  { id: 'typography', label: '🔤 Typography' }
]

const templates = [
  { id: 'classic', name: 'Classic', preview: 'linear-gradient(145deg, #1e293b, #020617)' },
  { id: 'bold', name: 'Bold', preview: 'linear-gradient(145deg, #7f1d1d, #1e3a8a)' },
  { id: 'minimal', name: 'Minimal', preview: 'linear-gradient(145deg, #f8fafc, #cbd5e1)' },
  { id: 'modern', name: 'Modern', preview: 'linear-gradient(145deg, #064e3b, #0c4a6e)' },
  { id: 'vibrant', name: 'Vibrant', preview: 'linear-gradient(145deg, #86198f, #831843)' },
  { id: 'dark', name: 'Dark', preview: 'linear-gradient(145deg, #0f172a, #000000)' }
]

const colorPresets = [
  '#020617', '#1e293b', '#0f172a', '#2d1a2d', '#1a2d2d',
  '#4c1d1d', '#1d3b4c', '#2d1d4c', '#1d4c3b', '#4c3b1d'
]

// Типы
type Carousel = {
  id: number
  title: string
  status: string
  language: string
  slides_count: number
  design?: any
}

type Slide = {
  id: number
  order: number
  title: string
  body: string
  footer: string | null
}

type Generation = {
  id: number
  status: string
  created_at: string
  error?: string
}

// Существующие переменные
const carousel = ref<Carousel | null>(null)
const slides = ref<Slide[]>([])
const activeSlideId = ref<number | null>(null)
const generationStatus = ref<string>('')
const exporting = ref(false)
const regenerating = ref(false)
const generations = ref<Generation[]>([])

const slideDom = ref<HTMLElement | null>(null)

// РАСШИРЕННЫЙ DESIGN ОБЪЕКТ
const design = reactive({
  template: 'classic',
  bgColor: '#020617',
  bgImageUrl: '',
  overlayOpacity: 50,
  padding: 80,
  alignment: 'left',
  valign: 'top',
  showHeader: true,
  headerText: '',
  showFooter: true,
  footerText: '',
  titleFontSize: 32,
  bodyFontSize: 18,
  fontFamily: 'system-ui'
})

// НОВЫЙ computed slideCanvasStyle
const slideCanvasStyle = computed(() => {
  const baseStyle: any = {
    width: '1080px',
    height: '1350px',
    padding: `${design.padding}px ${design.padding * 1.2}px`,
    boxSizing: 'border-box',
    borderRadius: '32px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: design.valign === 'top' ? 'flex-start' : design.valign === 'bottom' ? 'flex-end' : 'space-between',
    alignItems: design.alignment === 'left' ? 'flex-start' : design.alignment === 'right' ? 'flex-end' : 'center',
    textAlign: design.alignment,
    fontFamily: design.fontFamily,
    backgroundColor: design.bgColor,
    position: 'relative'
  }
  
  if (design.bgImageUrl) {
    baseStyle.backgroundImage = `linear-gradient(rgba(0,0,0,${design.overlayOpacity/100}), rgba(0,0,0,${design.overlayOpacity/100})), url(${design.bgImageUrl})`
    baseStyle.backgroundSize = 'cover'
    baseStyle.backgroundPosition = 'center'
  }
  
  return baseStyle
})

const activeSlide = computed({
  get() {
    return slides.value.find(s => s.id === activeSlideId.value) || null
  },
  set(val) {
    if (!val) return
    const idx = slides.value.findIndex(s => s.id === val.id)
    if (idx !== -1) slides.value[idx] = val
  }
})

const genStatusText = computed(() => generationStatus.value)

// НОВАЯ ФУНКЦИЯ СБРОСА
const resetDesign = () => {
  design.template = 'classic'
  design.bgColor = '#020617'
  design.bgImageUrl = ''
  design.overlayOpacity = 50
  design.padding = 80
  design.alignment = 'left'
  design.valign = 'top'
  design.showHeader = true
  design.headerText = ''
  design.showFooter = true
  design.footerText = ''
  design.titleFontSize = 32
  design.bodyFontSize = 18
  design.fontFamily = 'system-ui'
}

// Существующие функции
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

const fetchData = async () => {
  const id = Number(route.params.id)
  const [{ data: c }, { data: s }, { data: gen }] = await Promise.all([
    api.get<Carousel>(`/carousels/${id}`),
    api.get<Slide[]>(`/carousels/${id}/slides`),
    api.get<Generation[]>(`/generations/by-carousel/${id}`)
  ])
  carousel.value = c
  slides.value = s
  if (!activeSlideId.value && s.length) activeSlideId.value = s[0].id

  // Загружаем сохраненный дизайн если есть
  if (c.design) {
    Object.assign(design, c.design)
  }
  generations.value = gen
}

const saveActive = async () => {
  if (!activeSlide.value || !carousel.value) return
  const s = activeSlide.value
  await api.patch(`/carousels/${carousel.value.id}/slides/${s.id}`, {
    title: s.title,
    body: s.body,
    footer: s.footer
  })
}

const saveDesign = async () => {
  if (!carousel.value) return
  await api.patch(`/carousels/${carousel.value.id}`, {
    design: { ...design }
  })
}

const onUploadBg = async (e: Event) => {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return
  const file = input.files[0]

  const form = new FormData()
  form.append('file', file)

  const { data } = await axios.post<{ url: string }>(
    `${config.public.apiBase}/assets/upload`,
    form,
    {
      headers: {
        'X-API-Key': config.public.apiKey,
        'Content-Type': 'multipart/form-data'
      }
    }
  )
  design.bgImageUrl = data.url
}

const pollGeneration = async () => {
  const genId = route.query.generationId
  if (!genId) return
  const id = Number(genId)
  
  try {
    const source = new EventSource(`${config.public.apiBase}/generations/${id}/events`)
    source.onmessage = (event) => {
      generationStatus.value = event.data
      if (event.data === 'done' || event.data === 'failed') {
        source.close()
        fetchData()
      }
    }
  } catch (e) {
    const interval = setInterval(async () => {
      const { data } = await api.get(`/generations/${id}`)
      generationStatus.value = data.status
      if (data.status === 'done' || data.status === 'failed') {
        clearInterval(interval)
        fetchData()
      }
    }, 2000)
  }
}

const onExport = async () => {
  if (!carousel.value || !slides.value.length) return
  exporting.value = true
  try {
    const zip = new JSZip()
    for (const slide of slides.value) {
      activeSlideId.value = slide.id
      await nextTick()
      if (!slideDom.value) continue
      const canvas = await html2canvas(slideDom.value, {
        backgroundColor: design.bgColor,
        scale: 1,
        logging: false,
        allowTaint: true,
        useCORS: true
      })
      const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, 'image/png'))
      if (!blob) continue
      const arrayBuffer = await blob.arrayBuffer()
      zip.file(`slide_${slide.order.toString().padStart(2, '0')}.png`, arrayBuffer)
    }
    const content = await zip.generateAsync({ type: 'blob' })
    const url = URL.createObjectURL(content)
    const a = document.createElement('a')
    a.href = url
    a.download = `${carousel.value.title.replace(/\s+/g, '_').toLowerCase()}.zip`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Export failed:', e)
  } finally {
    exporting.value = false
  }
}

const statusClass = (status: string) => {
  if (status === 'done' || status === 'ready') return 'bg-emerald-900/60 text-emerald-300'
  if (status === 'queued' || status === 'running' || status === 'generating') return 'bg-amber-900/60 text-amber-300'
  if (status === 'failed') return 'bg-rose-900/60 text-rose-300'
  return 'bg-slate-800 text-slate-200'
}

const triggerRegenerate = async () => {
  if (!carousel.value) return
  regenerating.value = true
  try {
    const { data } = await api.post('/generations', { carousel_id: carousel.value.id })
    route.query.generationId = String(data.id)
    await pollGeneration()
  } finally {
    regenerating.value = false
  }
}

onMounted(async () => {
  await fetchData()
  await pollGeneration()
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #0f172a;
  border-top: 1px solid rgba(148, 163, 184, 0.15);
  padding: 0.75rem 1rem;
  z-index: 40;
  display: flex;
  justify-content: space-around;
}

@media (min-width: 640px) {
  .mobile-bottom-nav {
    display: none;
  }
}

@media (max-width: 640px) {
  .min-h-screen {
    padding-bottom: 80px;
  }
}

.scrollable-tabs {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  scrollbar-color: #4b5563 #1f2937;
}

.scrollable-tabs::-webkit-scrollbar {
  height: 4px;
}

.scrollable-tabs::-webkit-scrollbar-track {
  background: #1f2937;
  border-radius: 4px;
}

.scrollable-tabs::-webkit-scrollbar-thumb {
  background: #4b5563;
  border-radius: 4px;
}
</style>


slideDom