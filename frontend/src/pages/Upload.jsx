import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadAPI, handleAPIError, createFileFormData } from '../api/api'

/**
 * Upload Page Component
 * Handles CSV file uploads and data preview
 */
function Upload() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)
  
  const fileInputRef = useRef(null)
  const navigate = useNavigate()

  // Handle file selection
  const handleFileSelect = (file) => {
    if (file && file.type === 'text/csv') {
      setSelectedFile(file)
      setError('')
      setUploadResult(null)
    } else {
      setError('Please select a valid CSV file')
    }
  }

  // Handle file input change
  const handleFileInputChange = (e) => {
    const file = e.target.files[0]
    handleFileSelect(file)
  }

  // Handle drag events
  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  // Handle file drop
  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  // Handle file upload
  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first')
      return
    }

    setUploading(true)
    setError('')

    try {
      const formData = createFileFormData(selectedFile)
      const response = await uploadAPI.uploadCSV(formData)
      
      if (response.success) {
        setUploadResult(response)
        // Navigate to dashboard after successful upload
        setTimeout(() => {
          navigate('/dashboard')
        }, 2000)
      } else {
        setError(response.message || 'Upload failed')
      }
    } catch (err) {
      setError(handleAPIError(err, 'Upload failed. Please try again.'))
    } finally {
      setUploading(false)
    }
  }

  // Clear selected file
  const clearFile = () => {
    setSelectedFile(null)
    setUploadResult(null)
    setError('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="container">
      <div className="max-w-4xl mx-auto">
        <div className="mb-lg">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Upload Dataset
          </h1>
          <p className="text-gray-600">
            Upload a CSV file to analyze and make predictions
          </p>
        </div>

        {/* Upload Area */}
        <div className="card">
          {/* Drag and Drop Area */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? 'border-primary-color bg-primary-color bg-opacity-5'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="mb-4">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
            
            <div className="mb-4">
              <label htmlFor="file-upload" className="cursor-pointer">
                <span className="btn btn-primary">
                  Choose CSV File
                </span>
                <input
                  id="file-upload"
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  onChange={handleFileInputChange}
                  className="hidden"
                />
              </label>
              <p className="text-sm text-gray-600 mt-2">
                or drag and drop your CSV file here
              </p>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="alert alert-error mt-4">
              {error}
            </div>
          )}

          {/* Selected File Info */}
          {selectedFile && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">
                    {selectedFile.name}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
                <div className="flex gap-sm">
                  <button
                    onClick={clearFile}
                    className="btn btn-secondary"
                    disabled={uploading}
                  >
                    Clear
                  </button>
                  <button
                    onClick={handleUpload}
                    className="btn btn-primary"
                    disabled={uploading}
                  >
                    {uploading ? (
                      <>
                        <div className="loading mr-2"></div>
                        Uploading...
                      </>
                    ) : (
                      'Upload File'
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Upload Success */}
          {uploadResult && uploadResult.success && (
            <div className="mt-6">
              <div className="alert alert-success">
                <h3 className="font-medium mb-2">Upload Successful!</h3>
                <p className="text-sm">{uploadResult.message}</p>
                <p className="text-sm mt-2">
                  Redirecting to dashboard...
                </p>
              </div>
              
              {/* Data Preview */}
              <div className="mt-4">
                <h4 className="font-medium text-gray-900 mb-2">
                  Data Preview
                </h4>
                <div className="bg-gray-50 p-3 rounded-md overflow-x-auto">
                  <p className="text-sm text-gray-600 mb-2">
                    <strong>Columns:</strong> {uploadResult.file_info.columns.join(', ')}
                  </p>
                  <p className="text-sm text-gray-600">
                    <strong>Rows:</strong> {uploadResult.file_info.size}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="card mt-lg">
          <h3 className="font-medium text-gray-900 mb-3">
            Upload Instructions
          </h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-start">
              <span className="text-primary-color mr-2">•</span>
              Upload a CSV file with your data
            </li>
            <li className="flex items-start">
              <span className="text-primary-color mr-2">•</span>
              Ensure your data has clear column headers
            </li>
            <li className="flex items-start">
              <span className="text-primary-color mr-2">•</span>
              Include numeric columns for machine learning predictions
            </li>
            <li className="flex items-start">
              <span className="text-primary-color mr-2">•</span>
              Maximum file size: 16MB
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Upload
