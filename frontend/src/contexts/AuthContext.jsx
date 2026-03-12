import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../api/api'

/**
 * Authentication Context
 * Manages user authentication state throughout the application
 */
const AuthContext = createContext()

/**
 * AuthProvider Component
 * Provides authentication context to child components
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  // Check authentication status on component mount
  useEffect(() => {
    checkAuthStatus()
  }, [])

  /**
   * Check authentication status from localStorage
   */
  const checkAuthStatus = async () => {
    try {
      const storedToken = localStorage.getItem('garuda_token')
      const storedUser = localStorage.getItem('garuda_user')

      if (storedToken && storedUser) {
        // Verify token is still valid
        try {
          await authAPI.verifyToken(storedToken)
          
          // Token is valid, set auth state
          setToken(storedToken)
          setUser(JSON.parse(storedUser))
          setIsAuthenticated(true)
        } catch (error) {
          // Token is invalid, clear stored data
          clearAuthData()
        }
      }
    } catch (error) {
      console.error('Auth status check failed:', error)
      clearAuthData()
    } finally {
      setLoading(false)
    }
  }

  /**
   * Login user
   * @param {string} username - User username
   * @param {string} token - JWT token
   */
  const login = (username, token) => {
    const userData = { username }
    
    setUser(userData)
    setToken(token)
    setIsAuthenticated(true)
    
    // Store in localStorage
    localStorage.setItem('garuda_token', token)
    localStorage.setItem('garuda_user', JSON.stringify(userData))
  }

  /**
   * Logout user
   */
  const logout = async () => {
    try {
      // Call logout API (optional, as JWT tokens are stateless)
      if (token) {
        await authAPI.logout()
      }
    } catch (error) {
      console.error('Logout API call failed:', error)
    } finally {
      // Clear auth state regardless of API call success
      clearAuthData()
    }
  }

  /**
   * Clear authentication data
   */
  const clearAuthData = () => {
    setUser(null)
    setToken(null)
    setIsAuthenticated(false)
    
    // Clear localStorage
    localStorage.removeItem('garuda_token')
    localStorage.removeItem('garuda_user')
  }

  /**
   * Update user data
   * @param {Object} userData - Updated user data
   */
  const updateUser = (userData) => {
    setUser(prev => ({ ...prev, ...userData }))
    localStorage.setItem('garuda_user', JSON.stringify({ ...user, ...userData }))
  }

  const value = {
    user,
    token,
    isAuthenticated,
    loading,
    login,
    logout,
    updateUser,
    checkAuthStatus
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

/**
 * useAuth Hook
 * Custom hook to use authentication context
 * @returns {Object} Authentication context value
 */
export function useAuth() {
  const context = useContext(AuthContext)
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  
  return context
}

export default AuthContext
