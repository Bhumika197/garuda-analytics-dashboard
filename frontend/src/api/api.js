/**
 * Garuda Analytics Dashboard - API Service
 * Handles all HTTP requests to the backend API
 */

import axios from 'axios'

// API base URL - change this to match your backend server
const API_BASE_URL = 'http://localhost:5000'

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Request interceptor to add JWT token to headers
 */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('garuda_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response interceptor to handle common errors
 */
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle 401 Unauthorized - token expired or invalid
    if (error.response?.status === 401) {
      localStorage.removeItem('garuda_token')
      localStorage.removeItem('garuda_user')
      window.location.href = '/login'
    }
    
    // Handle network errors
    if (!error.response) {
      throw new Error('Network error. Please check your connection.')
    }
    
    // Handle other HTTP errors
    throw error.response.data?.message || error.message
  }
)

/**
 * Authentication API calls
 */
export const authAPI = {
  /**
   * Login user and get JWT token
   * @param {string} username - User username
   * @param {string} password - User password
   * @returns {Promise} Login response with token
   */
  login: async (username, password) => {
    const response = await api.post('/login', { username, password })
    return response.data
  },

  /**
   * Verify JWT token
   * @param {string} token - JWT token to verify
   * @returns {Promise} Token verification response
   */
  verifyToken: async (token) => {
    const response = await api.post('/auth/verify', { token })
    return response.data
  },

  /**
   * Logout user
   * @returns {Promise} Logout response
   */
  logout: async () => {
    const response = await api.post('/auth/logout')
    return response.data
  }
}

/**
 * Upload API calls
 */
export const uploadAPI = {
  /**
   * Upload CSV file
   * @param {FormData} formData - Form data with CSV file
   * @returns {Promise} Upload response with data analysis
   */
  uploadCSV: async (formData) => {
    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  /**
   * Get information about uploaded data
   * @returns {Promise} Data information response
   */
  getDataInfo: async () => {
    const response = await api.get('/api/data-info')
    return response.data
  },

  /**
   * Clear uploaded data from session
   * @returns {Promise} Clear data response
   */
  clearData: async () => {
    const response = await api.delete('/api/clear-data')
    return response.data
  }
}

/**
 * Prediction API calls
 */
export const predictionAPI = {
  /**
   * Run ML prediction on uploaded data
   * @param {Object} predictionConfig - Prediction configuration
   * @param {string} predictionConfig.targetColumn - Target column for prediction
   * @param {Array} predictionConfig.featureColumns - Feature columns for prediction
   * @param {string} predictionConfig.modelType - Type of ML model
   * @returns {Promise} Prediction response with results
   */
  predict: async (predictionConfig) => {
    const response = await api.post('/api/predict', predictionConfig)
    return response.data
  },

  /**
   * Get stored prediction results
   * @returns {Promise} Prediction results response
   */
  getPredictionResults: async () => {
    const response = await api.get('/api/prediction-results')
    return response.data
  },

  /**
   * Get information about trained model
   * @returns {Promise} Model information response
   */
  getModelInfo: async () => {
    const response = await api.get('/api/model-info')
    return response.data
  }
}

/**
 * Health check API call
 */
export const healthAPI = {
  /**
   * Check API health status
   * @returns {Promise} Health status response
   */
  check: async () => {
    const response = await api.get('/health')
    return response.data
  }
}

/**
 * Utility function to handle API errors consistently
 * @param {Error} error - Error object
 * @param {string} fallbackMessage - Fallback error message
 * @returns {string} User-friendly error message
 */
export const handleAPIError = (error, fallbackMessage = 'An error occurred') => {
  if (typeof error === 'string') {
    return error
  }
  
  if (error?.response?.data?.message) {
    return error.response.data.message
  }
  
  if (error?.message) {
    return error.message
  }
  
  return fallbackMessage
}

/**
 * Utility function to create FormData for file uploads
 * @param {File} file - File to upload
 * @returns {FormData} FormData object with file
 */
export const createFileFormData = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return formData
}

export default api
