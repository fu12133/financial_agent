import axios from 'axios'
import { AnalysisRequest, AnalysisResponse } from '../types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 300000,  // 5 minutes
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('📤 API Request:', config.method?.toUpperCase(), config.url)
    console.log('📤 Full URL:', config.baseURL + config.url)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('📥 API Response:', response.status, response.config.url)
    console.log('📥 Response Data:', response.data)
    return response.data
  },
  (error) => {
    console.error('❌ API Error:', error.response?.status, error.message)
    console.error('❌ Error Details:', error.response?.data)
    return Promise.reject(error)
  }
)

export const analysisAPI = {
  // Company analysis
  analyzeCompany: (data: AnalysisRequest): Promise<AnalysisResponse> => {
    return api.post('/analyze/company', data)
  },

  // Industry analysis
  analyzeIndustry: (data: AnalysisRequest): Promise<AnalysisResponse> => {
    return api.post('/analyze/industry', data)
  },

  // Chat conversation
  chat: (message: string, user_id: string = 'default'): Promise<any> => {
    return api.post('/chat', { message, user_id })
  },

  // Query news
  queryNews: (ticker: string, days: number = 7, limit: number = 10): Promise<any> => {
    return api.post('/news/query', { ticker, days, limit })
  },
}

export default api