import React from 'react'
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

/**
 * Layout Component
 * Provides navigation and common layout for authenticated pages
 */
function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  // Handle logout
  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // Check if a link is active
  const isActive = (path) => {
    return location.pathname === path
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/dashboard" className="flex items-center">
                <div className="text-xl font-bold text-primary-color">
                  🦅 Garuda Analytics
                </div>
              </Link>
            </div>

            {/* Navigation Links */}
            <nav className="hidden md:flex space-x-8">
              <Link
                to="/dashboard"
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  isActive('/dashboard')
                    ? 'text-primary-color bg-primary-color bg-opacity-10'
                    : 'text-gray-700 hover:text-primary-color hover:bg-gray-50'
                }`}
              >
                Dashboard
              </Link>
              <Link
                to="/upload"
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  isActive('/upload')
                    ? 'text-primary-color bg-primary-color bg-opacity-10'
                    : 'text-gray-700 hover:text-primary-color hover:bg-gray-50'
                }`}
              >
                Upload Data
              </Link>
            </nav>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <div className="text-sm">
                <span className="text-gray-600">Welcome, </span>
                <span className="font-medium text-gray-900">{user?.username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="btn btn-secondary text-sm"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Navigation */}
      <div className="md:hidden border-b border-gray-200 bg-white">
        <div className="container">
          <div className="flex space-x-8 overflow-x-auto py-2">
            <Link
              to="/dashboard"
              className={`px-3 py-2 text-sm font-medium rounded-md whitespace-nowrap transition-colors ${
                isActive('/dashboard')
                  ? 'text-primary-color bg-primary-color bg-opacity-10'
                  : 'text-gray-700 hover:text-primary-color hover:bg-gray-50'
              }`}
            >
              Dashboard
            </Link>
            <Link
              to="/upload"
              className={`px-3 py-2 text-sm font-medium rounded-md whitespace-nowrap transition-colors ${
                isActive('/upload')
                  ? 'text-primary-color bg-primary-color bg-opacity-10'
                  : 'text-gray-700 hover:text-primary-color hover:bg-gray-50'
              }`}
            >
              Upload Data
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="py-6">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="container py-4">
          <div className="text-center text-sm text-gray-500">
            <p>© 2024 Garuda Analytics Dashboard. Built with React, Flask, and Machine Learning.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout
