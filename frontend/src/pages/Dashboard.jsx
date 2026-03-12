import React, { useState, useEffect } from 'react'
import { predictionAPI, uploadAPI, handleAPIError } from '../api/api'
import Chart from '../components/Chart'

/**
 * Dashboard Page Component
 * Displays data analysis and ML predictions
 */
function Dashboard() {
  const [dataInfo, setDataInfo] = useState(null)
  const [predictionResults, setPredictionResults] = useState(null)
  const [modelInfo, setModelInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [predictionLoading, setPredictionLoading] = useState(false)
  const [error, setError] = useState('')
  const [predictionConfig, setPredictionConfig] = useState({
    targetColumn: '',
    featureColumns: []
  })

  // Load data and prediction results on component mount
  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    setError('')
    
    try {
      // Load data info
      const dataResponse = await uploadAPI.getDataInfo()
      if (dataResponse.success) {
        setDataInfo(dataResponse.data_info)
        
        // Set default target column (first numeric column)
        const numericColumns = dataResponse.data_info?.numeric_columns || []
        if (numericColumns.length > 0) {
          setPredictionConfig(prev => ({
            ...prev,
            targetColumn: numericColumns[0],
            featureColumns: numericColumns.slice(1) // Use other numeric columns as features
          }))
        }
      }
      
      // Load prediction results if available
      try {
        const predictionResponse = await predictionAPI.getPredictionResults()
        if (predictionResponse.success) {
          setPredictionResults(predictionResponse.prediction_results)
        }
      } catch (err) {
        // No prediction results available yet
      }
      
      // Load model info if available
      try {
        const modelResponse = await predictionAPI.getModelInfo()
        if (modelResponse.success) {
          setModelInfo(modelResponse.model_info)
        }
      } catch (err) {
        // No model trained yet
      }
      
    } catch (err) {
      setError(handleAPIError(err, 'Failed to load dashboard data'))
    } finally {
      setLoading(false)
    }
  }

  // Handle prediction configuration changes
  const handleConfigChange = (field, value) => {
    setPredictionConfig(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // Run prediction
  const runPrediction = async () => {
    if (!predictionConfig.targetColumn) {
      setError('Please select a target column')
      return
    }

    setPredictionLoading(true)
    setError('')

    try {
      const response = await predictionAPI.predict(predictionConfig)
      
      if (response.success) {
        setPredictionResults(response)
        setModelInfo({
          model_type: response.model_info.model_type,
          target_column: response.model_info.target_column,
          feature_columns: response.model_info.feature_columns,
          metrics: response.metrics,
          feature_importance: response.feature_importance
        })
      } else {
        setError(response.message || 'Prediction failed')
      }
    } catch (err) {
      setError(handleAPIError(err, 'Prediction failed. Please try again.'))
    } finally {
      setPredictionLoading(false)
    }
  }

  // Clear data
  const clearData = async () => {
    try {
      await uploadAPI.clearData()
      setDataInfo(null)
      setPredictionResults(null)
      setModelInfo(null)
      setError('')
    } catch (err) {
      setError(handleAPIError(err, 'Failed to clear data'))
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="text-center mt-lg">
          <div className="loading"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="mb-lg">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Analytics Dashboard
        </h1>
        <p className="text-gray-600">
          Analyze your data and run machine learning predictions
        </p>
      </div>

      {error && (
        <div className="alert alert-error mb-lg">
          {error}
        </div>
      )}

      {!dataInfo ? (
        <div className="card text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            No Data Available
          </h3>
          <p className="text-gray-600 mb-6">
            Please upload a CSV file to start analyzing your data
          </p>
          <a href="/upload" className="btn btn-primary">
            Upload Dataset
          </a>
        </div>
      ) : (
        <div className="space-y-lg">
          {/* Data Overview */}
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Data Overview
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Total Rows</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dataInfo.basic_info?.rows || 0}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Total Columns</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dataInfo.basic_info?.columns || 0}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Numeric Columns</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dataInfo.numeric_columns?.length || 0}
                </p>
              </div>
            </div>
            
            {/* Column Lists */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Numeric Columns</h4>
                <div className="bg-gray-50 p-3 rounded-md">
                  {dataInfo.numeric_columns?.length > 0 ? (
                    <ul className="text-sm text-gray-600 space-y-1">
                      {dataInfo.numeric_columns.map(col => (
                        <li key={col}>• {col}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-gray-500">No numeric columns found</p>
                  )}
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Categorical Columns</h4>
                <div className="bg-gray-50 p-3 rounded-md">
                  {dataInfo.categorical_columns?.length > 0 ? (
                    <ul className="text-sm text-gray-600 space-y-1">
                      {dataInfo.categorical_columns.map(col => (
                        <li key={col}>• {col}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-gray-500">No categorical columns found</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Prediction Configuration */}
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Machine Learning Prediction
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="form-group">
                <label className="form-label">Target Column</label>
                <select
                  value={predictionConfig.targetColumn}
                  onChange={(e) => handleConfigChange('targetColumn', e.target.value)}
                  className="form-select"
                >
                  <option value="">Select target column</option>
                  {dataInfo.numeric_columns?.map(col => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label">Feature Columns</label>
                <div className="bg-gray-50 p-3 rounded-md max-h-32 overflow-y-auto">
                  {dataInfo.numeric_columns?.filter(col => col !== predictionConfig.targetColumn).map(col => (
                    <label key={col} className="flex items-center text-sm">
                      <input
                        type="checkbox"
                        checked={predictionConfig.featureColumns.includes(col)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            handleConfigChange('featureColumns', [...predictionConfig.featureColumns, col])
                          } else {
                            handleConfigChange('featureColumns', predictionConfig.featureColumns.filter(c => c !== col))
                          }
                        }}
                        className="mr-2"
                      />
                      {col}
                    </label>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="flex gap-sm">
              <button
                onClick={runPrediction}
                className="btn btn-primary"
                disabled={predictionLoading || !predictionConfig.targetColumn}
              >
                {predictionLoading ? (
                  <>
                    <div className="loading mr-2"></div>
                    Running Prediction...
                  </>
                ) : (
                  'Run Prediction'
                )}
              </button>
              <button
                onClick={clearData}
                className="btn btn-secondary"
              >
                Clear Data
              </button>
            </div>
          </div>

          {/* Prediction Results */}
          {predictionResults && predictionResults.success && (
            <div className="card">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Prediction Results
              </h3>
              
              {/* Model Metrics */}
              {predictionResults.metrics && (
                <div className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-3">Model Performance</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">R² Score</p>
                      <p className="text-xl font-bold text-gray-900">
                        {predictionResults.metrics.r2_score?.toFixed(4) || 'N/A'}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Mean Squared Error</p>
                      <p className="text-xl font-bold text-gray-900">
                        {predictionResults.metrics.mean_squared_error?.toFixed(4) || 'N/A'}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Mean Absolute Error</p>
                      <p className="text-xl font-bold text-gray-900">
                        {predictionResults.metrics.mean_absolute_error?.toFixed(4) || 'N/A'}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Prediction Charts */}
              {predictionResults.predictions && (
                <div className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-3">Predictions Visualization</h4>
                  <Chart 
                    data={predictionResults.predictions.slice(0, 100)} 
                    targetColumn={predictionResults.target_column}
                  />
                </div>
              )}
              
              {/* Feature Importance */}
              {predictionResults.feature_importance && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Feature Importance</h4>
                  <div className="bg-gray-50 p-4 rounded-md">
                    <div className="space-y-2">
                      {predictionResults.feature_importance.features?.map((feature, index) => (
                        <div key={feature} className="flex items-center justify-between">
                          <span className="text-sm font-medium">{feature}</span>
                          <span className="text-sm text-gray-600">
                            {predictionResults.feature_importance.coefficients[index]?.toFixed(4)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Dashboard
