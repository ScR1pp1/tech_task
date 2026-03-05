import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  compatibilityDate: '2026-03-05', // Добавьте эту строку с сегодняшней датой
  typescript: {
    strict: true
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
      apiKey: process.env.NUXT_PUBLIC_API_KEY || 'dev-secret-key'
    }
  },
  css: ['~/assets/main.css']
})