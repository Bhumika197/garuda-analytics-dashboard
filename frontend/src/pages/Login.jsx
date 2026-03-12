import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI, handleAPIError } from '../api/api'
import { useAuth } from '../contexts/AuthContext'

/**
 * Login Page Component
 * Handles user authentication and JWT token management
 */
function Login() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const navigate = useNavigate()
  const { login } = useAuth()

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    // Clear error when user starts typing
    if (error) setError('')
  }

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validate form
    if (!formData.username || !formData.password) {
      setError('Please enter both username and password')
      return
    }

    setLoading(true)
    setError('')

    try {
      // Call login API
      const response = await authAPI.login(formData.username, formData.password)
      
      if (response.success) {
        // Store token and user info
        localStorage.setItem('garuda_token', response.token)
        localStorage.setItem('garuda_user', JSON.stringify({
          username: response.user.username,
          session: response.user.session
        }))
        
        // Update auth context
        login(response.user.username, response.token)
        
        // Navigate to dashboard
        navigate('/dashboard')
      } else {
        setError(response.message || 'Login failed')
      }
    } catch (err) {
      setError(handleAPIError(err, 'Login failed. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Garuda Analytics
          </h1>
          <p className="text-gray-600">
            Sign in to access your analytics dashboard
          </p>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Message */}
            {error && (
              <div className="alert alert-error">
                {error}
              </div>
            )}

            {/* Username Field */}
            <div className="form-group">
              <label htmlFor="username" className="form-label">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                value={formData.username}
                onChange={handleChange}
                className="form-input"
                placeholder="Enter your username"
                disabled={loading}
                required
              />
            </div>

            {/* Password Field */}
            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                className="form-input"
                placeholder="Enter your password"
                disabled={loading}
                required
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="btn btn-primary w-full"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="loading mr-2"></div>
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 text-center mb-3">
              Demo Credentials
            </p>
            <div className="bg-gray-50 p-3 rounded-md text-sm">
              <p><strong>Username:</strong> admin</p>
              <p><strong>Password:</strong> admin123</p>
              <p className="text-xs text-gray-500 mt-2">
                You can also use 'user/user123' or 'demo/demo123'
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          <p>Garuda Analytics Dashboard © 2024</p>
        </div>
      </div>
    </div>
  )
}

export default Login
