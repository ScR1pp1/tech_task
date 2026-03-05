import axios from 'axios'

export const useApi = () => {
  const config = useRuntimeConfig()

  const client = axios.create({
    baseURL: config.public.apiBase,
    headers: {
      'X-API-Key': config.public.apiKey
    }
  })

  return client
}

